# -*- coding: utf-8 -*-
from collections import defaultdict

from django.contrib.admin.utils import NestedObjects
from django.core.management import call_command
from django.template import Context, Template
from django.conf import settings

import os


DENIS_SH_TEMPLATE = """#!/bin/sh

if [ -z $MANAGE ]; then
    MANAGE={{ managepy }}
fi

{% for model in models %}
echo PROCESSING {{ model.name }}
$MANAGE loaddata {{ model.fixture }}
{% endfor %}
"""


class Denis(object):

    def __init__(self, qs, outdir, using, **kwargs):
        self.qs = qs
        self.output_dir = outdir
        self.using = using

        self.models = []
        self.objects = defaultdict(list)

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
        collector = NestedObjects(using=self.using)
        collector.collect(self.qs)
        objs = collector.nested()

        def model_name(obj):
            return "%s.%s" % (obj._meta.app_label, obj._meta.model_name)

        def collect_objects(obj):
            try:
                iter(obj)
                for o in obj:
                    collect_objects(o)
            except TypeError:
                name = model_name(obj)
                # FIXME: skip m2m tables!
                if name not in self.models and name not in self.models_blacklist:
                    self.models.append(name)
                self.objects[name].append(str(obj.pk))

        for obj in objs:
            collect_objects(obj)

    def dump(self):
        outdir = os.path.abspath(self.output_dir)
        try:
            os.mkdir(outdir)
        except OSError:
            pass
        except:
            raise

        def model_fixture(outdir, model, format):
            return os.path.join(outdir, '%s.%s' % (model, self.format))

        script = os.path.join(outdir, 'denis.sh')
        with open(script, 'w+') as f:
            self.collect()

            models = []
            for model in self.models:
                pks = ','.join(self.objects[model])
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
                models.append({
                    'name': model,
                    'fixture': output,
                })

            manage_path = os.path.join(os.path.abspath(settings.BASE_DIR), 'manage.py')
            template = Template(DENIS_SH_TEMPLATE)
            ctx = Context({'models': models, 'managepy': manage_path})
            f.write(template.render(ctx))
