import React, { useState, useEffect } from 'react';
import { Modal, ModalBody, ModalHeader, Row, Col, Alert } from 'reactstrap';
import { Field, useFormik, FormikHelpers, FormikProvider } from 'formik';
import { fetchUtil } from 'utils/fetchUtil';
import * as Yup from 'yup';
import { ExtensionRow } from 'hooks/admin';
import { useSubmitterDataPeriods, useEntities } from 'hooks/entities';
import QueryWrapper from 'core-wrappers/QueryWrapper';
import { convertPeriodLabelToApiValue } from 'utils/dateUtil';
import FieldWrapper from 'core-wrappers/FieldWrapperFormik';
import Button from 'core-components/Button';
import ExtensionFormInfo from 'apcd-components/Submitter/Extensions/ExtensionFormInfo';

interface EditExtensionModalProps {
  isVisible: boolean;
  onClose: () => void;
  extension: ExtensionRow | null;
  statusOptions: string[] | undefined;
  outcomeOptions: string[] | undefined;
  onEditSuccess?: (updatedExtension: ExtensionRow) => void;
}

interface FormValues {
  extensions: {
    businessName: string;
    extensionType: string;
    applicableDataPeriod: string;
    requestedTargetDate: string;
    currentExpectedDate: string;
  }[];
  requestorName: string;
  requestorEmail: string;
  justification: string;
  ext_outcome: string;
  ext_status: string;
  ext_id: string;
  approved_expiration_date: string;
  notes: string;
}

const EditExtensionModal: React.FC<EditExtensionModalProps> = ({
  isVisible,
  onClose,
  extension,
  statusOptions,
  outcomeOptions,
  onEditSuccess,
}) => {
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const [showErrorMessage, setShowErrorMessage] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [currentExtension, setCurrentExtension] = useState<ExtensionRow | null>(
    extension
  );

  const {
    data: submitterData,
    isLoading: submitterDataLoading,
    error: submitterDataError,
  } = useSubmitterDataPeriods(extension?.submitter_id);

  const {
    data: entitiesData,
    isLoading: entitiesLoading,
    isError: entitiesError,
  } = useEntities();

  useEffect(() => {
    setCurrentExtension(extension);
  }, [extension]);

  if (!currentExtension) return null;

  // Use the custom hook to get form fields and validation
  const useFormFields = () => {
    const initialValues: FormValues = {
      extensions: [
        {
          businessName: currentExtension.org_name,
          extensionType: currentExtension.type.toLowerCase().replace(" ", '_'),
          applicableDataPeriod: currentExtension.applicable_data_period,
          requestedTargetDate: currentExtension.requested_target_date,
          currentExpectedDate: currentExtension?.current_expected_date,
        },
      ],
      requestorName: currentExtension.requestor,
      requestorEmail: currentExtension.requestor_email,
      justification: currentExtension.explanation_justification,
      ext_outcome: currentExtension.ext_outcome,
      ext_status: currentExtension.ext_status,
      ext_id: currentExtension.ext_id,
      approved_expiration_date: currentExtension.approved_expiration_date,
      notes: currentExtension?.notes || 'None', // Set notes to 'None' if it is null
    };

    const validationSchema = Yup.object({
      justificiation: Yup.string()
        .max(2000, 'Notes cannot exceed 2000 characters')
        .nullable(),
      notes: Yup.string()
        .max(2000, 'Notes cannot exceed 2000 characters')
        .nullable(),
    });

    return { initialValues, validationSchema };
  };
  const { initialValues, validationSchema } = useFormFields();

  const onSubmit = async (
    values: FormValues,
    actions: FormikHelpers<FormValues>
  ) => {
    const { ext_id } = values;
    const api_values = {
      ...values,
      applicable_data_period: convertPeriodLabelToApiValue(
        values.extensions[0].applicableDataPeriod
      ),
    };
    const url = `administration/update-extension/${ext_id}/`;

    try {
      setShowSuccessMessage(false);
      setShowErrorMessage(false);
      const response = await fetchUtil({
        url,
        method: 'PUT',
        body: api_values,
      });

      if (response) {
        setCurrentExtension((prevExtension) => ({
          ...prevExtension!,
          ext_status: values.ext_status,
          ext_outcome: values.ext_outcome,
          applicable_data_period: values.extensions[0].applicableDataPeriod,
          approved_expiration_date: values.approved_expiration_date,
          notes: values.notes,
          updated_at: new Date().toISOString(),
        }));

        setShowSuccessMessage(true);
        if (onEditSuccess) onEditSuccess(response);
      }
    } catch (error: any) {
      if (error.response && error.response.data) {
        // Use error message from the server response
        setErrorMessage(
          error.response.data.message ||
            'An error occurred while saving the data. Please try again.'
        );
      } else {
        // Use generic error message
        setErrorMessage(
          'An error occurred while saving the data. Please try again.'
        );
      }
      setShowErrorMessage(true);
    } finally {
      actions.setSubmitting(false);
    }
  };

  const formik = useFormik<FormValues>({
    initialValues,
    validationSchema,
    onSubmit,
    enableReinitialize: true,
  });

  const handleClose = () => {
    setShowSuccessMessage(false);
    setShowErrorMessage(false);
    onClose();
  };

  const closeBtn = (
    <button className="close" onClick={onClose} type="button">
      &times;
    </button>
  );

  return (
    <>
      <Modal
        isOpen={isVisible}
        onClose={onClose}
        className="modal-dialog modal-lg"
      >
        <ModalHeader close={closeBtn}>
          Edit Extension ID {currentExtension.ext_id} for{' '}
          {currentExtension.org_name}
        </ModalHeader>
        <ModalBody>
          <QueryWrapper
            isLoading={submitterDataLoading}
            error={submitterDataError as Error}
          >
            <FormikProvider value={formik}>
              <form onSubmit={formik.handleSubmit}>
                {formik.values.extensions.map((extension, index) => (
                  <ExtensionFormInfo
                    key={index}
                    index={index}
                    submitterData={entitiesData}
                    isModal={true}
                  />
                ))}
                <Row>
                  <Col md={3}>
                    <FieldWrapper
                      name="extensions[0].applicableDataPeriod"
                      label="Applicable Data Period"
                      required={false}
                    >
                      <Field
                        as="select"
                        name="extensions[0].applicableDataPeriod"
                        id="extensions[0].applicableDataPeriod"
                        value={convertPeriodLabelToApiValue(
                          formik.values.extensions[0].applicableDataPeriod
                        )}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                          formik.setFieldValue(
                            `extensions[0].applicableDataPeriod`,
                            e.target.value
                          );
                          formik.setFieldValue(
                            `extensions[0].currentExpectedDate`,
                            submitterData?.data_periods?.find(
                              (p) => p.data_period === e.target.value
                            )?.expected_date
                          );
                        }}
                        onBlur={formik.handleBlur}
                      >
                        {submitterData?.data_periods?.map((item) => (
                          <option
                            key={item.data_period}
                            value={item.data_period}
                          >
                            {item.data_period}
                          </option>
                        ))}
                      </Field>
                      <div className="help-text">
                        Submitted: {currentExtension.applicable_data_period}
                      </div>
                    </FieldWrapper>
                  </Col>
                  <Col md={3}>
                    <FieldWrapper
                      name="approved_expiration_date"
                      label="Approved Expiration Date"
                      required={false}
                    >
                      <Field
                        type="date"
                        name="approved_expiration_date"
                        id="approved_expiration_date"
                        value={
                          formik.values.approved_expiration_date
                            ? formik.values.approved_expiration_date
                            : ''
                        }
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                      />
                    </FieldWrapper>
                  </Col>
                  <Col md={3}>
                    <FieldWrapper
                      name="ext_status"
                      label="Extension Status"
                      required={false}
                    >
                      <Field
                        as="select"
                        name="ext_status"
                        id="ext_status"
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        value={formik.values.ext_status}
                      >
                        {statusOptions?.map(
                          (opt) =>
                            opt.value !== 'All' && (
                              <option
                                className="dropdown-text"
                                key={opt.key}
                                value={opt.value}
                              >
                                {opt.value}
                              </option>
                            )
                        )}
                      </Field>
                    </FieldWrapper>
                  </Col>
                  <Col md={3}>
                    <FieldWrapper
                      name="ext_outcome"
                      label="Extension Outcome"
                      required={false}
                    >
                      <Field
                        as="select"
                        name="ext_outcome"
                        id="ext_outcome"
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        value={formik.values.ext_outcome}
                      >
                        {outcomeOptions?.map((opt) => (
                          <option
                            className="dropdown-text"
                            key={opt.key}
                            value={opt.value}
                          >
                            {opt.value}
                          </option>
                        ))}
                      </Field>
                    </FieldWrapper>
                  </Col>
                  <Col md={6}>
                    <FieldWrapper
                      name="justification"
                      label="Justification"
                      required={false}
                    >
                      <Field
                        as="textarea"
                        name="justification"
                        id="justification"
                        rows="5"
                        maxLength="2000" // Set the maxLength attribute
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                      />
                      <div className="help-text">2000 character limit</div>
                    </FieldWrapper>
                  </Col>
                  <Col md={6}>
                    <FieldWrapper name="notes" label="Notes" required={false}>
                      <Field
                        as="textarea"
                        name="notes"
                        id="notes"
                        rows="5"
                        maxLength="2000" // Set the maxLength attribute
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                      />
                      <div className="help-text">2000 character limit</div>
                    </FieldWrapper>
                  </Col>
                </Row>
                <br />
                <Alert color="success" isOpen={showSuccessMessage}>
                  Success: The extension data has been successfully updated.
                </Alert>
                <Alert color="danger" isOpen={showErrorMessage}>
                  Error: {errorMessage}
                </Alert>
                <Button
                  type="primary"
                  attr="submit"
                  disabled={!formik.dirty || formik.isSubmitting}
                >
                  Submit
                </Button>
              </form>
            </FormikProvider>
          </QueryWrapper>
        </ModalBody>
      </Modal>
    </>
  );
};

export default EditExtensionModal;
