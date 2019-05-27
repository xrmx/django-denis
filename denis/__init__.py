# -*- coding: utf-8 -*-
from django.contrib.admin.utils import NestedObjects


class Denis(object):

    def __init__(self, qs, using, **kwargs):
        self.qs = qs
        self.using = using

    def collect(self):
        def collect_objects(obj):
            try:
                iter(obj)
                for o in obj:
                    collect_objects(o)
            except TypeError:
                flattened.append(obj)

        collector = NestedObjects(using=self.using)
        collector.collect(self.qs)
        objs = collector.nested()
        flattened = []

        for obj in objs:
            collect_objects(obj)

        return flattened

    def recover(self, using):
        objects = self.collect()
        obj_per_model = {}
        models = []
        non_concrete_models = set()

        for obj in objects:
            model_name = obj._meta.model_name
            if obj._meta.concrete_model in non_concrete_models:
                continue
            if model_name not in obj_per_model:
                # we cannot bulk_create multi-table inherited models
                non_concrete_parents = [
                    parent for parent in obj._meta.get_parent_list()
                        if parent._meta.concrete_model is not obj._meta.concrete_model
                ]
                for parent in non_concrete_parents:
                    non_concrete_models.add(parent)
                obj_per_model[model_name] = {
                    'class': type(obj),
                    'non_concrete_parents': non_concrete_parents,
                    'objs': [],
                }
                models.append(model_name)
            obj_per_model[model_name]['objs'].append(obj)

        # remove models that are parent of others
        concrete_models = (m for m in models if m not in non_concrete_models)
        for model in concrete_models:
            m = obj_per_model[model]
            klass = m['class']
            # we cannot bulk_create multi-table inherited models, for other use plain save
            if not m['non_concrete_parents']:
                klass.objects.using(using).bulk_create(m['objs'])
            else:
                for obj in m['objs']:
                    obj.save(using=using)
