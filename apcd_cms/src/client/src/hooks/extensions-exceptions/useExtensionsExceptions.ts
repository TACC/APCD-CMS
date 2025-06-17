import { useQuery, UseQueryResult } from 'react-query';
import { fetchUtil } from 'utils/fetchUtil';
import {
  ExtensionResult,
  ExceptionResult,
} from '.';

const getSubmitterExtensions = async (params: any) => {
  const url = `submissions/extension/api/`;
  const response = await fetchUtil({
    url,
    params,
  });
  return response.response;
};

const getSubmitterExceptions = async (params: any) => {
  const url = `submissions/exception/api/`;
  const response = await fetchUtil({
    url,
    params,
  });
  return response.response;
};

export const useSubmitterExtensions = (
  status?: string,
  org?: string,
  page?: number
): UseQueryResult<ExtenionResult> => {
  const params: { status?: string; org?: string; page?: number } = {
    status,
    org,
    page,
  };
  const query = useQuery(['submitter-extensions', params], () =>
    getSubmitterExtensions(params)
  ) as UseQueryResult<ExtensionResult>;

  return { ...query };
};

export const useSubmitterExceptions = (
  status?: string,
  org?: string,
  page?: number
): UseQueryResult<ExceptionResult> => {
  const params: { status?: string; org?: string; page?: number } = {
    status,
    org,
    page,
  };
  const query = useQuery(['submitter-exceptions', params], () =>
    getSubmitterExceptions(params)
  ) as UseQueryResult<ExceptionResult>;

  return { ...query };
};