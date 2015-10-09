# -*- coding: utf-8 -*-
from collections import defaultdict

from django.contrib.admin.utils import NestedObjects
from django.core.management import call_command
from django.template import Context, Template
from django.conf import settings

import json
import os


DENIS_SH_TEMPLATE = """#!/bin/sh

if [ -z $MANAGE ]; then
    MANAGE={{ managepy }}
fi

{% for model in models %}
echo PROCESSING {{ model.name }}
$MANAGE loaddata --database {{ database }} {{ model.fixture }}
{% endfor %}
"""


class Denis(object):

    def __init__(self, qs, outdir, using, **kwargs):
        self.qs = qs
        self.output_dir = outdir
        self.using = using

        self.models_blacklist = kwargs.get('blacklist')
        if not self.models_blacklist:
            self.models_blacklist = []

        # dumpdata options
        self.indent = kwargs.get('indent')
        if not self.indent:
            self.indent = 2
        self.format = kwargs.get('format')
        if not self.format:
            self.format = 'json'

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

    def _parse_collected_objects(self, objects):
        def model_name(obj):
            return "%s.%s" % (obj._meta.app_label, obj._meta.model_name)

        def get_m2m_fields(model):
            return [
                f.name for f in model._meta.get_fields()
                    if (f.many_to_many and not f.auto_created)
            ]

        models = []
        objects_ids = defaultdict(list)
        m2m_fields = {}

        for obj in objects:
            name = model_name(obj)
            if name not in models and name not in self.models_blacklist:
                models.append(name)

                m2ms = get_m2m_fields(obj)
                m2m_fields[name] = m2ms
            objects_ids[name].append(str(obj.pk))

        return models, objects_ids, m2m_fields

    def dump(self, database=None):
        outdir = os.path.abspath(self.output_dir)
        try:
            os.mkdir(outdir)
        except OSError:
            pass
        except:
            raise

        if not database:
            database = 'default'

        def model_fixture(outdir, model, format):
            return os.path.join(outdir, '%s.%s' % (model, self.format))

        script = os.path.join(outdir, 'denis.sh')
        with open(script, 'w+') as f:
            flat_models = self.collect()
            models, objects_ids, m2m_fields = self._parse_collected_objects(flat_models)

            models_to_dump = []
            for model in models:
                pks = ','.join(objects_ids[model])
                output = model_fixture(outdir, model, self.format)
                if os.path.exists(output):
                    os.unlink(output)

                opts = {
                    'primary_keys': pks,
                    'output': output,
                    'format': self.format,
                    'database': self.using,
                    'indent': self.indent,
                    'exclude': [],
                }
                call_command('dumpdata', model, **opts)
                models_to_dump.append({
                    'name': model,
                    'fixture': output,
                })

                # we need to remove m2m fields from models in order to avoid
                # double insertions errors
                if model in m2m_fields:
                    fixture_f = open(output, 'r')
                    fixture = json.load(fixture_f)
                    fixture_f.close()

                    with open(output, 'w') as fixture_f:
                        for instance in fixture:
                            for field in m2m_fields[model]:
                                instance['fields'][field] = []
                        json.dump(fixture, fixture_f)

            manage_path = os.path.join(os.path.abspath(settings.BASE_DIR), 'manage.py')
            template = Template(DENIS_SH_TEMPLATE)
            ctx = Context({'models': models_to_dump, 'managepy': manage_path, 'database': database})
            f.write(template.render(ctx))
