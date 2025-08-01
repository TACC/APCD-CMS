from django.http import JsonResponse
from django.views.generic.base import TemplateView
from apps.utils import apcd_database
from apps.utils.apcd_groups import has_apcd_group
from apps.base.base import BaseAPIView, APCDGroupAccessAPIMixin, APCDGroupAccessTemplateMixin
import logging
import json
from datetime import date as datetimeDate
from datetime import datetime
from apps.utils.utils import table_filter
from apps.utils.utils import title_case
from apps.components.paginator.paginator import paginator

logger = logging.getLogger(__name__)


class ExtensionFormTemplate(APCDGroupAccessTemplateMixin, TemplateView):
    template_name = 'extension_submission_form/extension_submission_form.html'

class ExtensionListTemplate(APCDGroupAccessTemplateMixin, TemplateView):
    template_name = 'extension_submission_form/extension_list.html'

class ExtensionFormApi(APCDGroupAccessAPIMixin, BaseAPIView):

    def get(self, request):
        if (request.user.is_authenticated and has_apcd_group(request.user)):
            formatted_extension_data = []
            submitter_codes = []
            # submitter_id = request.GET.get('s_id', None)
            submitters = apcd_database.get_submitter_info(request.user.username)
            submitter_codes = []

            for submitter in submitters:
                submitter_codes.append(submitter[1])

            formatted_extension_data = apcd_database.get_all_extensions(submitter_codes=submitter_codes)

            context = self.get_extensions_list_json(formatted_extension_data)
            return JsonResponse({'response': context})
        else:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

    def get_extensions_list_json(self, extensions, *args, **kwargs):
        context = {}

        context['header'] = ['Created', 'Entity Organization - Payor Code', 'Requestor Name', 'Extension Type',
                             'Outcome', 'Status', 'Approved Expiration', 'Actions']
        context['status_options'] = ['All',
                                     'Pending']  # 'Pending' is default filter value on page load, need to have it hard-coded to not miss option once we reach client-side
        context['org_options'] = ['All']
        context['outcome_options'] = []
        context['extensions'] = []
        context['action_options'] = ['Select Action', 'View Record']

        try:
            page_num = int(self.request.GET.get('page'))
        except:
            page_num = 1

        def getDate(row):
            date = row[9]
            return date if date is not None else datetime(1, 1,
                                                          1)  # put 'None' date entries all together at end of listing w/ date 1-1-0001

        extensions = sorted(extensions, key=lambda row: getDate(row), reverse=True)

        extensions_table_entries = []

        for extension in extensions:
            extensions_table_entries.append(self._set_extension(extension))
            context['extensions'].append(self._set_extension(extension))

            entity_name = title_case(extension[18])
            status = title_case(extension[7]) if extension[7] else "None"
            outcome = title_case(extension[8])
            if entity_name not in context['org_options']:
                context['org_options'].append(entity_name)
                context['org_options'] = sorted(context['org_options'], key=lambda x: (x != 'All', x))
                # Remove empty strings
                context['org_options'] = [option for option in context['org_options'] if option != '']
            if status not in context['status_options']:
                context['status_options'].append(status)
                context['status_options'] = sorted(context['status_options'], key=lambda x: (x != 'All', x))
            if outcome not in context['outcome_options']:
                context['outcome_options'].append(outcome)
                context['outcome_options'] = sorted(context['outcome_options'],
                                                    key=lambda x: (x is not None, x))

        queryStr = ''
        status_filter = self.request.GET.get('status')
        org_filter = self.request.GET.get('org')

        context['selected_status'] = ''
        if status_filter is not None and status_filter != 'All':
            context['selected_status'] = status_filter
            queryStr += f'&status={status_filter}'
            extensions_table_entries = table_filter(status_filter, extensions_table_entries, 'ext_status')

        context['selected_org'] = ''
        if org_filter is not None and org_filter != 'All':
            context['selected_org'] = org_filter
            queryStr += f'&org={org_filter}'
            extensions_table_entries = table_filter(org_filter.replace("(", "").replace(")", ""),
                                                    extensions_table_entries, 'org_name')

        context['query_str'] = queryStr
        page_info = paginator(page_num, extensions_table_entries)
        context['page'] = [{'org_name': obj['org_name'], 'created': obj['created'], 'type': obj['type'],
                            'requestor': obj['requestor'],
                            'ext_outcome': obj['ext_outcome'], 'ext_status': obj['ext_status'],
                            'ext_id': obj['ext_id'], 'submitter_id': obj['submitter_id'],
                            'approved_expiration_date': obj['approved_expiration_date'],
                            'current_expected_date': obj['current_expected_date'],
                            'requested_target_date': obj['requested_target_date'],
                            'applicable_data_period': obj['applicable_data_period'],
                            'updated_at': obj['updated_at'], 'submitter_code': obj['submitter_code'],
                            'payor_code': obj['payor_code'], 'requestor_email': obj['requestor_email'],
                            'explanation_justification': obj['explanation_justification']} for obj in page_info['page']]

        context['page_num'] = page_num
        context['total_pages'] = page_info['page'].paginator.num_pages
        context['pagination_url_namespaces'] = 'extension:extension-list'
        return context

    def _set_extension(self, ext):
        return {
            'org_name': ext[18] if ext[18] else "None",
            'created': ext[9] if ext[9] else "None",
            'type': title_case(ext[5].replace('_', ' ')) if ext[5] else "None",
            'requestor': title_case(ext[14]) if ext[14] else "None",
            'ext_outcome': title_case(ext[8]) if ext[8] else "None",
            'ext_status': title_case(ext[7]) if ext[7] else "None",
            'ext_id': ext[0],
            'submitter_id': ext[1],
            'approved_expiration_date': ext[4] if ext[4] else "None",
            'current_expected_date': ext[2] if ext[2] else "None",
            'requested_target_date': ext[3] if ext[3] else "None",
            'applicable_data_period': self._get_applicable_data_period(ext[6]) if ext[6] else "None",
            'updated_at': ext[10] if ext[10] else "None",
            'submitter_code': ext[11] if ext[11] else "None",
            'payor_code': ext[12] if ext[12] else "None",
            'requestor_email': ext[15] if ext[15] else "None",
            'explanation_justification': ext[16] if ext[16] else "None",
        }

    # function converts int value in the format YYYYMM to a string with abbreviated month and year
    def _get_applicable_data_period(self, value):
        try:
            return datetime.strptime(str(value), '%Y%m').strftime('%b. %Y')
        except:
            return None

    def post(self, request):
        """
        Handle form submission and return JSON response for success/failure
        """
        form = json.loads(request.body)
        extensions = form['extensions']
        errors = []
        submitters = apcd_database.get_submitter_info(request.user.username)
        for extension in extensions:
            submitter = next(submitter for submitter in submitters if int(submitter[0] == int(extension['businessName'])))
            exten_resp = apcd_database.create_extension(form, extension, submitter)
            if self._err_msg(exten_resp):
                errors.append(self._err_msg(exten_resp))

        # Return success or error as JSON
        if errors:
            logger.error("Extension request failed. Errors: %s", errors)
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
        else:
            return JsonResponse({'status': 'success'}, status=200)

    def _err_msg(self, resp):
        """
        Helper function to extract error messages
        """
        if hasattr(resp, 'pgerror'):
            return resp.pgerror
        if isinstance(resp, Exception):
            return str(resp)
        return None
