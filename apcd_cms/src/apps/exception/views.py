from django.http import JsonResponse
from django.views.generic import TemplateView
from apps.utils import apcd_database
from apps.utils.apcd_groups import has_apcd_group
from apps.base.base import BaseAPIView, APCDGroupAccessAPIMixin, APCDGroupAccessTemplateMixin
import logging
import json
from apps.utils.utils import title_case, table_filter
from apps.components.paginator.paginator import paginator
from dateutil import parser

logger = logging.getLogger(__name__)


class ExceptionFormTemplate(APCDGroupAccessTemplateMixin, TemplateView):
    template_name = 'exception_submission_form.html'

class ExceptionListTemplate(APCDGroupAccessTemplateMixin, TemplateView):
    template_name = 'exception_list.html'

class ExceptionFormApi(APCDGroupAccessAPIMixin, BaseAPIView):

    def get(self, request):
        if (request.user.is_authenticated and has_apcd_group(request.user)):
            formatted_exception_data = []
            submitter_codes = []
            # submitter_id = request.GET.get('s_id', None)
            submitters = apcd_database.get_submitter_info(request.user.username)
            submitter_codes = []

            for submitter in submitters:
                submitter_codes.append(submitter[1])

            formatted_exception_data = apcd_database.get_all_exceptions(submitter_codes=submitter_codes)
            context = self.get_exception_list_json(formatted_exception_data)
            return JsonResponse({'response': context})
        else:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

    def get_exception_list_json(self, exception_content, *args, **kwargs):
        context = {}

        context['header'] = ['Created', 'Entity Organization - Payor Code', 'Requestor Name', 'Exception Type', 'Outcome', 'Status', 'Actions']
        context['status_options'] = ['All', 'Pending']
        context['org_options'] = ['All']
        context['outcome_modal_options'] = ['None', 'Granted', 'Denied', 'Withdrawn']
        context['status_modal_options'] = ['None', 'Complete', 'Pending']
        context['exceptions'] = []
        context['action_options'] = ['Select Action', 'View Record']

        try:
            page_num = int(self.request.GET.get('page'))
        except:
            page_num = 1

        queryStr = ''
        status_filter = self.request.GET.get('status')
        org_filter = self.request.GET.get('org')
        def _set_exception(exception):
            return {
                'exception_id': exception[0],
                'submitter_id': exception[1],
                'requestor_name': exception[2],
                'request_type': title_case(exception[3]) if exception[3] else None, # to make sure if val doesn't exist, utils don't break page
                'explanation_justification': exception[4],
                'outcome': title_case(exception[5]) if exception[5] else 'None',
                'outcome': title_case(exception[5]) if exception[5] else 'None',
                'created_at': exception[6],
                'updated_at': exception[7],
                'submitter_code': exception[8],
                'payor_code': exception[9],
                'user_id': exception[10],
                'requestor_email': exception[11],
                'data_file': exception[12],
                'field_number': exception[13],
                'required_threshold': exception[14],
                'requested_threshold': exception[15],
                'requested_expiration_date': exception[16],
                'approved_threshold': exception[17],
                'approved_expiration_date': exception[18],
                'status': title_case(exception[19]) if exception[19] else 'None',
                'entity_name': exception[21],
                'data_file_name': exception[22],
                'view_modal_content': {
                    'exception_id': exception[0],
                    'created_at':  exception[6],
                    'requestor_name': exception[2],
                    'requestor_email': exception[11],
                    'request_type': title_case(exception[3]) if exception[3] else None,
                    'status': title_case(exception[19]) if exception[3] else None,
                    'outcome': title_case(exception[5]) if exception[3] else None,
                    'data_file_name': exception[22],
                    'field_number': exception[13],
                    'required_threshold': exception[14],
                    'requested_threshold': exception[15],
                    'approved_threshold': exception[17],
                    'requested_expiration_date': exception[16],
                    'approved_expiration_date': exception[18],
                    'explanation_justification': exception[4],
                    'entity_name': exception[21],
                    'payor_code': exception[9],
                    'updated_at': exception[7],
                }
            }
        def getDate(row):
            date = row[6]
            return date if date is not None else parser.parse('1-1-0001')

        # sort exceptions by newest to oldest
        exception_content = sorted(exception_content, key=lambda row:getDate(row), reverse=True)

        limit = 50
        offset = limit * (page_num - 1)

        exception_table_entries = []
        for exception in exception_content:
            # to be used by paginator
            exception_table_entries.append(_set_exception(exception))
            # to be able to access any exception in a template using exceptions var in the future
            context['exceptions'].append(_set_exception(exception))
            entity_name = title_case(exception[21])
            status = title_case(exception[19]) if exception[19] else 'None'
            outcome = title_case(exception[5]) if exception[5] else 'None'
            if entity_name not in context['org_options']:
                context['org_options'].append(entity_name)
                # to make sure All is first in the dropdown filter options after sorting alphabetically
                context['org_options'] = sorted(context['org_options'], key=lambda x: (x != 'All', x))
                # Remove empty strings
                context['org_options'] = [option for option in context['org_options'] if option != '']
            if status not in context['status_options']:
                if status != None:
                    context['status_options'].append(status)
                    # to make sure All is first in the dropdown filter options after sorting alphabetically
                    context['status_options'] = sorted(context['status_options'], key=lambda x: (x != 'Pending', x))

        context['selected_status'] = None
        if status_filter is not None and status_filter != 'All':
            context['selected_status'] = status_filter
            queryStr += f'&status={status_filter}'
            exception_table_entries = table_filter(status_filter, exception_table_entries, 'status')

        context['selected_org'] = None
        if org_filter is not None and org_filter != 'All':
            context['selected_org'] = org_filter
            queryStr += f'&org={org_filter}'
            exception_table_entries = table_filter(org_filter.replace("(", "").replace(")",""), exception_table_entries, 'entity_name')

        context['query_str'] = queryStr
        page_info = paginator(page_num, exception_table_entries, limit)
        context['page'] = [{'entity_name': obj['entity_name'], 'payor_code': obj['payor_code'], 'created_at': obj['created_at'], 'request_type': obj['request_type'],
                            'requestor_name': obj['requestor_name'], 'outcome': obj['outcome'], 'status': obj['status'],
                            'approved_threshold': obj['approved_threshold'],'approved_expiration_date': obj['approved_expiration_date'],
                            'exception_id': obj['exception_id'], 'view_modal_content': obj['view_modal_content'],
                            'requested_threshold': obj['requested_threshold'],}
                            for obj in page_info['page']]

        context['page_num'] = page_num
        context['total_pages'] = page_info['page'].paginator.num_pages

        context['pagination_url_namespaces'] = 'admin_exception:list-exceptions'

        return context

    def post(self, request):
        form = json.loads(request.body)
        errors = []
        exception_type = form['exceptionType'].lower()
        # Though type other exceptions don't have the need to submit multiple exception requests in one form,
        # passing in exceptions object so the shared functionality of formik form fields can be used on 
        # the front end for both threshold and other exceptions for validation schemas
        exceptions = form['exceptions']
        if exception_type == 'threshold':
            submitters = apcd_database.get_submitter_info(request.user.username)
            for exception in exceptions:
                submitter = next(submitter for submitter in submitters if int(submitter[0] == int(exception['businessName'])))
                exception_response = apcd_database.create_threshold_exception(form, exception, submitter)
                if self._err_msg(exception_response):
                    errors.append(self._err_msg(exception_response))
            if len(errors) != 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to process exceptions',
                    'errors': errors, # Will display in response what field failed to post in DB
                    'code': 'THRESHOLD_EXCEPTION_DB_ERROR'
                }, status=500)
            return JsonResponse({'status': 'success', 'message': 'Exception submission successful'}, status=200)
        
        if exception_type == 'other':
            submitters = apcd_database.get_submitter_info(request.user.username)
            for exception in exceptions:
                submitter = next(submitter for submitter in submitters if int(submitter[0] == int(exception['businessName'])))
                other_exception_response = apcd_database.create_other_exception(form, exception, submitter)
                if self._err_msg(other_exception_response):
                    errors.append(self._err_msg(other_exception_response))
            if len(errors) != 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to process exceptions',
                    'errors': errors, # Will display in response what field failed to post in DB
                    'code': 'OTHER_EXCEPTION_DB_ERROR'
                }, status=500)
            return JsonResponse({'status': 'success', 'message': 'Exception submission successful'}, status=200)
        
    def _err_msg(self, resp):
        if hasattr(resp, 'pgerror'):
            return resp.pgerror
        if isinstance(resp, Exception):
            return str(resp)
        return None
