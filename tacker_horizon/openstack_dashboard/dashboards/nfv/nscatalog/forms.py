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


from django.core.urlresolvers import reverse
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from tacker_horizon.openstack_dashboard import api

import yaml
import re

class CreateSFC(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"), required=False)

    source_type = forms.ChoiceField(
        label=_('VNFFG Source'),
        required=False,
        choices=[('file', _('TOSCA Template File')),
                 ('raw', _('Create SFC'))],
        widget=forms.Select(
            attrs={'class': 'switchable', 'data-slug': 'source'}))

    toscal_file = forms.FileField(
        label=_("VNFFG TOSCA Template File"),
        help_text=_("A local TOSCA template file to upload."),
        widget=forms.FileInput(
            attrs={'class': 'switched', 'data-switch-on': 'source',
                   'data-source-file': _('TOSCA Template File')}),
        required=False)

    vnf1 = forms.ChoiceField(
        label=_('Create SFC from VNFs'),
        help_text=_('Select VNFs to chain together'),
        choices=[('dummyVNF1', 'dummyVNF1'),
                 ('dummyVNF2', 'dummyVNF2')],
        widget=forms.Select(
            attrs={'class': 'switched', 'data-switch-on': 'source',
                   'data-source-raw': _('VNF1')}),
        required=False)

    vnf2 = forms.ChoiceField(
        label=_('Create SFC from VNFs'),
        help_text=_('Select VNFs to chain together'),
        choices=[('dummyVNF1', 'dummyVNF1'),
                 ('dummyVNF2', 'dummyVNF2')],
        widget=forms.Select(
            attrs={'class': 'switched', 'data-switch-on': 'source',
                   'data-source-raw': _('VNF2')}),
        required=False)


    def __init__(self, request, *args, **kwargs):
        super(CreateSFC, self).__init__(request, *args, **kwargs)

        try:
            vnf_list = api.tacker.vnf_list(request)
            available_choices = [(vnf['id'], vnf['name'])
                                 for vnf in vnf_list]
        except Exception as e:
            msg = _('Failed to retrieve available VNF Instances: %s') % e
            LOG.error(msg)

        self.fields['vnf1'].choices = [('', _('Select a VNF Instance Name'))
                                          ]+available_choices
        self.fields['vnf2'].choices = [('', _('Select a VNF Instance Name'))
                                          ]+available_choices
    def clean(self):
        data = super(CreateSFC, self).clean()

        # The key can be missing based on particular upload
        # conditions. Code defensively for it here...
        toscal_file = data.get('toscal_file', None)
        sfc_chain = [data.get(vnf_field, None) for vnf_field in ['vnf1', 'vnf2']]

        if sfc_chain and toscal_file:
            raise ValidationError(
                _("Cannot specify both file and direct chain."))
        if not sfc_chain and not toscal_file:
            raise ValidationError(
                _("No input was provided for the namespace content."))
        try:
            if toscal_file:
                toscal_str = self.files['toscal_file'].read()
                data['tosca'] = toscal_str
            else:
                data['sfc'] = sfc_chain
        except Exception as e:
            msg = _('There was a problem loading the namespace: %s.') % e
            raise forms.ValidationError(msg)

        return data

    def handle(self, request, data):
        try:
            if 'tosca' in data:
                print "Inside TOSCA for SFC.  Does not work yet: "
                messages.success(request,
                                _('This does not work yet.'))
            else:
                # this is a list of vnf ids
                sfc_data = data['sfc']
                # Need to pass IP of node, and service type
                # may also need to get neutron port id
                sfc_dict = dict()
                for vnf in sfc_data:
                    vnf_result = api.tacker.get_vnf(request, vnf)
                    vnf_data = vnf_result['vnf']
                    sfc_dict[vnf] = dict()
                    # find IP in mgmt_url string
                    sfc_dict[vnf]['ip'] = re.search(r'[0-9]+(?:\.[0-9]+){3}', vnf_data['mgmt_url']).group()
                    # trozet check here to see how services are passed
                    # we can only specify 1 atm for ODL
                    sfc_dict[vnf]['type'] = vnf_data['attributes']['service_type']
                    # we also need the neutron port ID
                    # tacker doesnt find this so we can use the vnf id to find the
                    # neutron port as it is listed in the name
                    port_output = api.tacker.list_neutron_ports(request)
                    for port in port_output['ports']:
                        if port['name'].find(vnf_data['id']) > 0:
                            sfc_dict[vnf]['neutron_port_id'] = port['id']
                    if 'neutron_port_id' not in sfc_dict[vnf]:
                        raise KeyError('Unable to find neutron_port_id')
                sfc_arg = {'sfc': sfc_dict}
                # Passes vnf IDs to create sfc
                # Order of list determines chain order
                api.tacker.create_sfc(request, sfc_arg)
                messages.success(request,
                             _('SFC has been created.'))
            return True
        except Exception as e:
            exceptions.handle(request,
                              _('Unable to create SFC.'))
            return False