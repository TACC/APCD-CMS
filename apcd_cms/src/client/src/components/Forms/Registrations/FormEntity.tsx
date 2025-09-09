import React from 'react';
import { Field, ErrorMessage } from 'formik';
import { FormGroup, Label, FormFeedback } from 'reactstrap';
import { TextFormField } from './TextFormField';
import styles from './RegistrationForm.module.css';
import FieldWrapper from 'core-wrappers/FieldWrapperFormik';

const getPayorTypes = (posted_date: Date | null) => {
  // UTHealth's registration year begins Oct 1 of the previous year
  // ex. reg year 2026 will begin 10/01/2025, so allow 2026 starting that day
  const sep15_25 = new Date(`2025-09-15 0:00:00`);
  if (posted_date && posted_date < sep15_25) {
    return ['Commercial', 'Medicare', 'Medicaid'];
  }
  return ['Commerical', 'Medicare_Advantage', 'Medicare_Supplementary', 'Medicaid'];
}

export const RegistrationEntity: React.FC<{ index: number, posted_date: Date | null, isEdit: boolean }> = ({ index, posted_date, isEdit }) => {
  return (
    <div>
      <h5 className={`${styles.boldedHeader} ${styles.spacedHeader}`}>
        ENTITY {index + 1}
      </h5>
      <TextFormField
        name={`entities.${index}.entity_name`}
        label="Name"
        required={true}
      />

      <FieldWrapper
        name={`entities.${index}.number_code`}
        label="Number/Code"
        required={true}
        description="Provide all available identifiers. At least one of the following is required."
      >
        <div id={`entities-${index}.number_code`} style={{ display: 'none' }} />
        <FormGroup className="o-grid o-grid--col-auto-count" noMargin={true}>
          <TextFormField
            name={`entities.${index}.fein`}
            label="FEIN²"
            helpText="Enter in format 12-3456789."
          />

          <TextFormField
            name={`entities.${index}.license_number`}
            label="License Number"
            helpText="Enter digits only."
          />

          <TextFormField
            name={`entities.${index}.naic_company_code`}
            label="NAIC³ Company Code"
            helpText="Enter digits only."
          />
        </FormGroup>
      </FieldWrapper>

      <h6 className={styles.boldedHeader}>Type of Payor</h6>
      <FieldWrapper
        name={`entities.${index}.types_of_payors_hidden`}
        label="Payor Types"
        required={true}
      >
        <div
          id={`entities.${index}.types_of_payors_hidden`}
          style={{ display: 'none' }}
        />
        <FormGroup
          className="checkboxselectmultiple"
          id={`entities.${index}.types_of_payors`}
        >
          {getPayorTypes(posted_date).map((payorType) => (
            <FormGroup
              key={`entities.${index}.types_of_payors_${payorType.toLowerCase()}.wrapper`}
              noMargin={true}
            >
              <Label
                htmlFor={`entities.${index}.types_of_payors_${payorType.toLowerCase()}`}
                key={`entities.${index}.types_of_payors_${payorType.toLowerCase()}.label`}
              >
                <Field
                  type="checkbox"
                  key={`entities.${index}.types_of_payors_${payorType.toLowerCase()}`}
                  name={`entities.${index}.types_of_payors_${payorType.toLowerCase()}`}
                  id={`entities.${index}.types_of_payors_${payorType.toLowerCase()}`}
                ></Field>
                {payorType.replace('_',' ')}
                {payorType == 'Medicaid' ? (
                  <small>(for state use only)</small>
                ) : (
                  <></>
                )}
              </Label>
            </FormGroup>
          ))}
        </FormGroup>
      </FieldWrapper>

      <h6 className={styles.boldedHeader}>File Submission</h6>
      <FieldWrapper
        name={`entities.${index}.types_of_files_hidden`}
        label="Types of Files"
        required={true}
        description="Eligibility/Enrollment and Provider files are mandatory. At least one claims file type (Medical, Pharmacy, and Dental) must be selected."
      >
        <FormGroup
          className="checkboxselectmultiple"
          id={`entities.${index}.types_of_files`}
        >
          {[
            'Eligibility/Enrollment',
            'Provider',
            'Medical',
            'Pharmacy',
            'Dental',
          ].map((fileType) => (
            <FormGroup
              key={`entities.${index}.types_of_files_${fileType
                .toLowerCase()
                .replace('/', '_')}.wrapper`}
              noMargin={true}
            >
              <Label
                htmlFor={`entities.${index}.types_of_files_${fileType
                  .toLowerCase()
                  .replace('/', '_')}`}
                key={`entities.${index}.types_of_files_${fileType
                  .toLowerCase()
                  .replace('/', '_')}.label`}
              >
                <Field
                  type="checkbox"
                  key={`entities.${index}.types_of_files_${fileType
                    .toLowerCase()
                    .replace('/', '_')}`}
                  name={`entities.${index}.types_of_files_${fileType
                    .toLowerCase()
                    .replace('/', '_')}`}
                  id={`entities.${index}.types_of_files_${fileType
                    .toLowerCase()
                    .replace('/', '_')}`}
                  disabled={fileType == 'Eligibility/Enrollment' || fileType == 'Provider' ? true : false}
                ></Field>
                {fileType}
              </Label>
            </FormGroup>
          ))}
        </FormGroup>
      </FieldWrapper>

      <h6 className={styles.boldedHeader}>
        Coverage Estimates
        <small>
          {' '}
          (Inclusive of all claims as of December 31 of previous year.)
        </small>
      </h6>

      <TextFormField
        name={`entities.${index}.total_covered_lives`}
        label="Total Covered Lives"
        required={true}
      />
      <TextFormField
        name={`entities.${index}.claims_encounters_volume`}
        label="Claims and Encounters Volume"
        helpText="Enter a whole number."
        required={true}
      />
      <TextFormField
        name={`entities.${index}.total_claims_value`}
        label="Total Claims Value (USD)⁴"
        required={true}
      />
    </div>
  );
};
