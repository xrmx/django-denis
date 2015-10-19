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

        for obj in objects:
            model_name = obj._meta.model_name
            if model_name not in obj_per_model:
                obj_per_model[model_name] = {
                    'class': type(obj),
                    'objs': []
                }
            obj_per_model[model_name]['objs'].append(obj)
            models.append(model_name)

        for model in models:
            m = obj_per_model[model]
            klass = m['class']
            klass.objects.using(using).bulk_create(m['objs'])
