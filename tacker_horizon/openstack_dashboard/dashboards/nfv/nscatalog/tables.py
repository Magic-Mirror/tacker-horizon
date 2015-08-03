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
from django.utils.translation import ungettext_lazy

from horizon import tables

from openstack_dashboard import policy
from tacker_horizon.openstack_dashboard import api

class MyFilterAction(tables.FilterAction):
    name = "myfilter"

class DeleteSFCLink(policy.PolicyTargetMixin, tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete SFC",
            u"Delete SFCs",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Delete SFC",
            u"Delete SFCs",
            count
        )

    def action(self, request, obj_id):
        api.tacker.delete_sfc(request,obj_id)

class OnBoardSFCLink(tables.LinkAction):
    name = "onboardsfc"
    verbose_name = _("Create SFC")
    classes = ("ajax-modal",)
    icon = "plus"
    url = "horizon:nfv:vnfcatalog:onboardvnf"


class VNFCatalogTable(tables.DataTable):
    name = tables.Column('name', \
                         verbose_name=_("Name"))
    description = tables.Column('description', \
                           verbose_name=_("Description"))
    services = tables.Column('services', \
                         verbose_name=_("Services"))
    id = tables.Column('id', \
                         verbose_name=_("Catalog Id"))

    class Meta:
        name = "vnfcatalog"
        verbose_name = _("VNFCatalog")
        table_actions = (OnBoardVNFLink, DeleteVNFLink, MyFilterAction,)
