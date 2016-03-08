# Copyright 2015 Brocade Communications System, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


from django.utils.translation import ugettext_lazy as _

import uuid

from horizon import exceptions
from horizon import tabs

from tacker_horizon.openstack_dashboard import api
from tacker_horizon.openstack_dashboard.dashboards.nfv.nscatalog import tables


class NSCatalogItem(object):
    def __init__(self, name, description, services, sfc_id):
        self.id = sfc_id
        self.name = name
        self.description = description
        self.services = services


class NSCatalogTab(tabs.TableTab):
    name = _("NSCatalog Tab")
    slug = "nscatalog_tab"
    table_classes = (tables.NSCatalogTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_nscatalog_data(self):
        try:
            # marker = self.request.GET.get(
            #            tables.VNFCatalogTable._meta.pagination_param, None)

            self._has_more = False
            instances = []
            print "SFC list API"
            sfcs = api.tacker.sfc_list(self.request)
            print "SFCs: " + str(sfcs)
            for sfc in sfcs:
                print "SFC entry " + str(sfc)
                print "SFC name " + sfc['name']
                print "SFC id " + sfc['id']
                print "SFC desc " + sfc['description']
                services = sfc['service_types']
                print "SFC Services: " + str(services)
                sfc_services =[]
                for s in services:
                    print "Serv:" + str(s)
                    if s['service_type'] != 'sfc':
                        sfc_services.append(s['service_type'])
                print "SFCService: " + str(sfc_services)
                sfcs_services_string = ""
                if len(sfc_services) > 0:
                    sfcs_services_string = ', '.join([str(item) for item in sfc_services])
                item = NSCatalogItem(sfc['name'], sfc['description'], sfcs_services_string, sfc['id'])
                instances.append(item)
            print "Instances: " + str(instances)
            return instances
        except Exception:
            self._has_more = False
            error_message = _('Unable to get instances')
            exceptions.handle(self.request, error_message)

            return []


class NSCatalogTabs(tabs.TabGroup):
    slug = "nscatalog_tabs"
    tabs = (NSCatalogTab,)
    sticky = True
