import abc
import logging
import os
import re
import enum
from typing import List

import dedupe
from taggit.models import Tag

from curator.models import CanonicalTagMapping, CanonicalTag, TagCluster


class AbstractTagDeduper(abc.ABC):
    TRAINING_FILE = "curator/clustering_training.json"
    FIELDS = [{"field": "name", "type": "String"}]

    def uncertain_pairs(self):
        return self.deduper.uncertain_pairs()

    def mark_pairs(self, pairs, is_distinct: bool):
        labelled_examples = {"match": [], "distinct": []}

        example_key = "distinct" if is_distinct else "match"
        labelled_examples[example_key] = pairs

        self.deduper.mark_pairs(labelled_examples)

    def prepare_training_data(self):
        tags = Tag.objects.all().values()
        data = {row["id"]: row for i, row in enumerate(tags)}
        return data

    def console_label(self):
        dedupe.console_label(self.deduper)

    def training_file_exists(self) -> bool:
        return os.path.exists(self.TRAINING_FILE)

    def remove_training_file(self):
        if os.path.isfile(self.TRAINING_FILE):
            os.remove(self.TRAINING_FILE)

    def save_to_training_file(self):
        with open(self.TRAINING_FILE, "w") as file:
            self.deduper.write_training(file)


class TagClusterManager:
    def reset():
        TagCluster.objects.all().delete()

    def has_unlabelled_clusters():
        return TagCluster.objects.exists()

    def modify_cluster(tag_cluster: TagCluster):
        action = ""
        while action != "q":
            TagClusterManager.__display_cluster(tag_cluster)
            action = input(
                "What would you like to do?\n(c)hange canonical tag name\n(a)dd tags\n(r)emove tags\n(s)ave\n(f)inish\n"
            )

            if action == "c":
                new_canonical_tag_name = input("What would you like to change it to?\n")
                tag_cluster.canonical_tag_name = new_canonical_tag_name
            elif action == "a":
                tag_name = input("Input the name of the tag you would like to add\n")
                if not tag_cluster.add_tag_by_name(tag_name):
                    print("The tag does not exist in Tags")
            elif action == "r":
                tag_index = input(
                    "Input the number of the tag you would like to remove.\n"
                )

                tags = list(tag_cluster.tags.all())
                if not tag_index.isnumeric() or int(tag_index) >= len(tags):
                    print("Index is out of bounds!")
                    continue

                tags.pop(int(tag_index))
                tag_cluster.tags.set(tags)
            elif action == "s":
                print("Published mapping")
                canonical_tag, tag_mappings = tag_cluster.save_mapping()

                print(
                    f"The following was saved to the database: \n<CanonicalTag {canonical_tag}>\n{tag_mappings}"
                )

            elif action == "f":
                tag_cluster.delete()
                break
            else:
                print("Invalid option!")

    def console_label():
        if not TagCluster.objects.exists():
            logging.info("There aren't any clusters to label.")
            return

        tag_clusters = TagCluster.objects.all()
        for index, tag_cluster in enumerate(tag_clusters):
            TagClusterManager.modify_cluster(tag_cluster)

    def console_canonicalize_edit():
        quit = False
        while not quit:
            action = input(
                "What would you like to do?\n(v)iew canonical list\n(m)odify canonical tag\n(q)uit\n"
            )
            if action == "v":
                canonical_tags = CanonicalTag.objects.all()

                print("Canonical Tag List:")
                for canonical_tag in canonical_tags:
                    print(canonical_tag.name)
                print("")

            elif action == "m":
                name = input("Which one would you like to modify?\n")
                canonical_tag = CanonicalTag.objects.filter(name=name)
                tags = list(
                    CanonicalTagMapping.objects.filter(canonical_tag__in=canonical_tag)
                )

                if canonical_tag.exists():
                    tag_action = ""
                    while tag_action != "q":
                        print("\n\nCanonical tag:", canonical_tag[0].name)
                        print("Tags:")
                        for tag in tags:
                            if tag.canonical_tag == canonical_tag[0]:
                                print(tag.tag.name)
                        tag_action = input(
                            "What would you like to do?\n(a)dd tags\n(r)emove tags\n(s)ave\n(q)uit\n"
                        )

                        if tag_action == "a":
                            tag_name = input("Enter tag name:\n")
                            tag_to_add = Tag.objects.filter(name=tag_name)

                            if tag_to_add.exists():
                                canonical_tag_mapping = CanonicalTagMapping(
                                    tag=tag_to_add[0],
                                    canonical_tag=canonical_tag[0],
                                    confidence_score=1,
                                )
                                tags.append(canonical_tag_mapping)
                            else:
                                print("Tag cannot be found in database!")
                        elif tag_action == "r":
                            tag_name = input("Enter tag name:\n")

                            for tag in tags:
                                if tag.tag.name == tag_name:
                                    tag.canonical_tag = None
                        elif tag_action == "s":
                            for tag in tags:
                                tag.save()
                        elif tag_action == "q":
                            break

                else:
                    print("Canonical tag not found!")

            elif action == "q":
                quit = True

    def __display_cluster(tag_cluster: TagCluster):
        tag_names = [tag.name for tag in tag_cluster.tags.all()]
        print("Canonical tag name:", tag_cluster.canonical_tag_name, end="\n\n")
        print("Tags:")
        for index, tag_name in enumerate(tag_names):
            print(f"{index}. {tag_name}")
        print("")


class TagClusterer(AbstractTagDeduper):
    def __init__(self, clustering_threshold):
        self.clustering_threshold = clustering_threshold

        self.deduper = dedupe.Dedupe(AbstractTagDeduper.FIELDS)
        self.prepare_training()

    # The training data is stored in a file.
    # If it exists, load from the file
    # Otherwise, start from scratch
    def prepare_training(self):
        data = self.prepare_training_data()
        if os.path.exists(TagClusterer.TRAINING_FILE):
            with open(TagClusterer.TRAINING_FILE, "r") as training_file:
                self.deduper.prepare_training(data, training_file)
        else:
            self.deduper.prepare_training(data)

    # The model is trained and then the data is clustered
    def cluster_tags(self):
        self.deduper.train()
        return self.deduper.partition(
            self.prepare_training_data(), self.clustering_threshold
        )

    # Saves the clusters to the database
    def save_clusters(self, clusters):
        for id_list, confidence_list in clusters:
            tags = Tag.objects.filter(id__in=id_list)
            confidence_score = confidence_list[0]

            tag_cluster = TagCluster(
                canonical_tag_name=tags[0].name, confidence_score=confidence_score
            )
            tag_cluster.save()

            tag_cluster.tags.set(tags)
            tag_cluster.save()

    def save_to_training_file(self):
        with open(TagClusterer.TRAINING_FILE, "w") as file:
            self.deduper.write_training(file)

    def training_file_exists(self) -> bool:
        return os.path.exists(TagClusterer.TRAINING_FILE)

    def remove_training_file(self):
        if os.path.isfile(TagClusterer.TRAINING_FILE):
            os.remove(TagClusterer.TRAINING_FILE)


class TagGazetteer(AbstractTagDeduper):
    def __init__(self, search_threshold):
        self.search_threshold = search_threshold

        self.deduper = dedupe.Gazetteer(AbstractTagDeduper.FIELDS)
        self.prepare_training()

    # The training data is stored in a file.
    # If it exists, load from the file
    # Otherwise, start from scratch
    def prepare_training(self):
        data = self.prepare_training_data()
        canonical_data = self.prepare_canonical_data()

        if self.training_file_exists():
            with open(TagGazetteer.TRAINING_FILE, "r") as training_file:
                self.deduper.prepare_training(data, canonical_data, training_file)
        else:
            self.deduper.prepare_training(data, canonical_data)

    def prepare_canonical_data(self):
        tags = CanonicalTag.objects.all().values()
        data = {row["id"]: {**row} for i, row in enumerate(tags)}
        return data

    def search(self, data):
        self.deduper.train()
        self.deduper.index(self.prepare_canonical_data())
        return self.deduper.search(data, threshold=self.search_threshold)

    def text_search(self, name: str):
        results = self.search({1: {"id": 1, "name": name}})
        matches = results[0][1]

        matches = [
            (CanonicalTag.objects.filter(pk=match[0])[0], match[1]) for match in matches
        ]

        return matches
