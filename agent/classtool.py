
import os
from typing import Callable, Dict, Optional, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from dotenv import load_dotenv

load_dotenv()



class Account_opening_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: dict = Field(default={}, description='Argument api_args')

def account_opening_api_caller(api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None ) -> dict:
        """
        The api_caller function handles all scenarios that need an API according to
        your dataset. You can call this function with a specific api_name and any
        relevant api_args (if required for that scenario). It then returns a JSON
        object describing the result or data for that operation.

        Below is the list of recognized api_name values, along with a brief
        description of what each does, possible api_args, and what the return
        JSON looks like.

        1) "lead_not_found_in_saathi"
           ----------------------------------------------------
           Description:
             Checks if a lead exists in the Saathi system for a given client code
             and returns information about the lead status.
           Expected api_args:
             {
               "client_code": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "leadFound": bool,
                 "message": str
               }
             }

        2) "why_pan_already_exists"
           ----------------------------------------------------
           Description:
             Verifies if a given PAN is already present in the system.
           Expected api_args:
             {
               "pan_number": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "panStatus": "Duplicate" or "Unique",
                 "message": str
               }
             }

        3) "provide_zoom_link_non_individual"
           ----------------------------------------------------
           Description:
             Retrieves Zoom link details for non-individual account opening.
           Expected api_args: {}
           Return (example):
             {
               "status": "success",
               "data": {
                 "zoomMeetingID": str,
                 "meetingPasscode": str,
                 "message": str
               }
             }

        4) "checklist_for_individual"
           ----------------------------------------------------
           Description:
             Returns information on where to locate the checklist or form
             for opening an individual account.
           Expected api_args: {}
           Return (example):
             {
               "status": "success",
               "data": {
                 "checklistPath": str,
                 "message": str
               }
             }

        5) "checklist_for_non_individual"
           ----------------------------------------------------
           Description:
             Returns details on where to locate the checklist or form
             for non-individual account opening.
           Expected api_args: {}
           Return (example):
             {
               "status": "success",
               "data": {
                 "checklistPath": str,
                 "message": str
               }
             }

        6) "why_acop_form_rejected"
           ----------------------------------------------------
           Description:
             Fetches reasons why an ACOP physical form was rejected
             in the audit/inspection process.
           Expected api_args:
             {
               "client_code": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "rejectionReason": str,
                 "message": str
               }
             }

        7) "kyc_non_compliance_clarification"
           ----------------------------------------------------
           Description:
             Looks up the reasons for a KYC non-compliance objection.
           Expected api_args:
             {
               "client_code": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "objectionDetail": str,
                 "message": str
               }
             }

        8) "ipv_not_found"
           ----------------------------------------------------
           Description:
             Checks if an IPV code or name is present.
           Expected api_args:
             {
               "ipv_code": str,
               "ipv_name": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "ipvFound": bool,
                 "message": str
               }
             }

        9) "email_mobile_validation_link"
           ----------------------------------------------------
           Description:
             Validates whether an email/mobile verification link was sent.
           Expected api_args:
             {
               "client_code": str,
               "email": str,
               "mobile": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "linkDispatched": bool,
                 "message": str
               }
             }

        10) "segment_activation_status"
           ----------------------------------------------------
           Description:
             Retrieves the status of segment activation for a given client code.
           Expected api_args:
             {
               "client_code": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "activatedSegments": [str],
                 "message": str
               }
             }

        11) "where_to_check_sample_form"
           ----------------------------------------------------
           Description:
             Returns directions for where to locate a sample form.
           Expected api_args: {}
           Return (example):
             {
               "status": "success",
               "data": {
                 "pathInfo": str,
                 "message": str
               }
             }

        12) "code_blocked_iaa"
           ----------------------------------------------------
           Description:
             Checks details if a code is blocked for IAA despite KRA being validated.
           Expected api_args:
             {
               "client_code": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "blockedReason": str,
                 "message": str
               }
             }

        13) "nri_dormant_activation"
           ----------------------------------------------------
           Description:
             Retrieves instructions or status for reactivating a dormant NRI account.
           Expected api_args:
             {
               "client_code": str,
               "location": "abroad" or "india"
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "documentsRequired": [str],
                 "message": str
               }
             }

        14) "dormant_status_online"
           ----------------------------------------------------
           Description:
             Checks the status of a dormant account reactivation request placed online.
           Expected api_args:
             {
               "client_code": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "dormantStatus": "Active" or "Pending",
                 "message": str
               }
             }

        15) "dormant_status_offline"
           ----------------------------------------------------
           Description:
             Checks the status of a dormant reactivation request placed offline.
           Expected api_args:
             {
               "sr_number": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "reactivationProgress": str,
                 "message": str
               }
             }

        16) "check_objection_new_account"
           ----------------------------------------------------
           Description:
             Looks up objection details for a new account application.
           Expected api_args:
             {
               "client_code": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "currentObjection": str,
                 "message": str
               }
             }

        17) "check_objection_modification"
           ----------------------------------------------------
           Description:
             Looks up objection details for a modification request.
           Expected api_args:
             {
               "client_code": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "currentObjection": str,
                 "message": str
               }
             }

        18) "clear_objection_new_account"
           ----------------------------------------------------
           Description:
             Indicates the steps taken to clear an objection raised for a new account.
           Expected api_args:
             {
               "client_code": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "objectionCleared": bool,
                 "message": str
               }
             }

        19) "clear_objection_modification"
           ----------------------------------------------------
           Description:
             Indicates how an objection for a modification was cleared.
           Expected api_args:
             {
               "client_code": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "objectionCleared": bool,
                 "message": str
               }
             }

        20) "clear_objection_closure"
           ----------------------------------------------------
           Description:
             States how an objection for a closure request was resolved.
           Expected api_args:
             {
               "client_code": str
             }
           Return (example):
             {
               "status": "success",
               "data": {
                 "objectionCleared": bool,
                 "message": str
               }
             }

        21) "what_is_my_objection"
           ----------------------------------------------------
           Description:
             Retrieves a direct objection description tied to a client code.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "objectionDetail": str,
                 "message": str
               }
             }

        22) "why_objection_raised"
           ----------------------------------------------------
           Description:
             Explains the cause for an objection that has been raised.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "causeOfObjection": str,
                 "message": str
               }
             }

        23) "cvl_kra_valid_but_iaa"
           ----------------------------------------------------
           Description:
             Checks if CVL KRA is valid but the account is still in IAA status.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "activationPendingReason": str,
                 "message": str
               }
             }

        24) "why_dp_freeze"
           ----------------------------------------------------
           Description:
             Retrieves the reason a DP is frozen for a given client code.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "freezeReason": str,
                 "message": str
               }
             }

        25) "why_ac_suspended_iaa"
           ----------------------------------------------------
           Description:
             Provides reasons why an account is suspended due to IAA/KYC non-compliance.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "suspensionReason": str,
                 "message": str
               }
             }

        26) "kra_validated_but_cannot_trade"
           ----------------------------------------------------
           Description:
             Checks if KRA is validated but the client still cannot trade, possibly
             awaiting system updates or RMS checks.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "canTrade": bool,
                 "message": str
               }
             }

        27) "kra_validation_failure"
           ----------------------------------------------------
           Description:
             Provides instructions or status about a failed KRA validation.
           Expected api_args:
             {
               "pan_number": str,
               "mobile": str,
               "email": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "validationLink": str,
                 "message": str
               }
             }

        28) "invalid_pan"
           ----------------------------------------------------
           Description:
             Explains or checks if the provided PAN is invalid in the system.
           Expected api_args:
             {
               "pan_number": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "panValid": bool,
                 "message": str
               }
             }

        29) "segment_status_check"
           ----------------------------------------------------
           Description:
             Another way to see how segment activation is proceeding or completed.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "activationDetails": [str],
                 "message": str
               }
             }

        30) "why_new_ac_tba"
           ----------------------------------------------------
           Description:
             Reveals why a new account is showing as TBA (to be activated).
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "remainingSteps": str,
                 "message": str
               }
             }

        31) "why_account_status_iaa"
           ----------------------------------------------------
           Description:
             Clarifies why an account status is IAA while DP status is not frozen.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "suspensionCause": str,
                 "message": str
               }
             }

        32) "when_will_activate"
           ----------------------------------------------------
           Description:
             Tells how much time is left until the account is activated.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "activationETA": str,
                 "message": str
               }
             }

        33) "why_dp_activation_pending"
           ----------------------------------------------------
           Description:
             Returns the reason why DP activation is still pending for an account.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "pendingReason": str,
                 "message": str
               }
             }

        34) "why_validation_error"
           ----------------------------------------------------
           Description:
             Investigates a validation error the user may be seeing
             during or after account activation.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "errorDetails": str,
                 "message": str
               }
             }

        35) "dispatch_details_not_showing"
           ----------------------------------------------------
           Description:
             Checks why dispatch details for a courier are not visible in CBOS 2.0.
           Expected api_args:
             {
               "client_code": str,
               "dispatchType": str  # e.g., "ACOP", "MODIFICATION", "CLOSURE"
             }
           Return:
             {
               "status": "success",
               "data": {
                 "foundDispatch": bool,
                 "message": str
               }
             }

        37) "courier_received_confirmation"
           ----------------------------------------------------
           Description:
             Confirms whether a courier was received at the HO.
           Expected api_args:
             {
               "packet_number": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "courierReceived": bool,
                 "message": str
               }
             }

        38) "courier_dispatched_not_ack"
           ----------------------------------------------------
           Description:
             Checks if a dispatched courier is still awaiting acknowledgement.
           Expected api_args:
             {
               "packet_number": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "acknowledged": bool,
                 "message": str
               }
             }

        39) "code_not_reflecting_in_dispatch"
           ----------------------------------------------------
           Description:
             Checks why a particular code does not show in courier dispatch records.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "isCodeListed": bool,
                 "message": str
               }
             }

        40) "why_ekyc_ac_tba"
           ----------------------------------------------------
           Description:
             Explains why an eKYC-based account is still at TBA status.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "activationPendingReason": str,
                 "message": str
               }
             }

        41) "single_holder_rejected_to_ekyc"
           ----------------------------------------------------
           Description:
             Indicates that single-holder accounts must use eKYC, clarifies
             why CBOS punching was rejected.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "requiredProcess": "EKYC",
                 "message": str
               }
             }

        42) "not_able_to_request_kyc_form"
           ----------------------------------------------------
           Description:
             Explains or processes requests for a KYC form if the user cannot request it
             from CBOS 2.0.
           Expected api_args:
             {
               "form_type": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "formAccess": bool,
                 "message": str
               }
             }

        43) "i_want_my_acop_form"
           ----------------------------------------------------
           Description:
             Retrieves the ACOP form or the path to it, often from the
             client dashboard.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "acopFormLink": str,
                 "message": str
               }
             }

        44) "where_check_kyc_scan"
           ----------------------------------------------------
           Description:
             Informs where a user can find or view the KYC scan associated
             with their account.
           Expected api_args:
             {
               "client_code": str
             }
           Return:
             {
               "status": "success",
               "data": {
                 "kycScanAvailable": bool,
                 "scanPath": str,
                 "message": str
               }
             }
        """

        # A simple example structure. Each scenario returns a JSON representing
        # the result of that call. Replace or extend as necessary.

        print("kra_validated_but_cannot_trade")
        if api_name == "lead_not_found_in_saathi":
            response = {
                "status": "success",
                "data": {
                    "leadFound": False,
                    "message": "No lead found under the provided client_code.",
                },
            }
        elif api_name == "why_pan_already_exists":
            response = {
                "status": "success",
                "data": {
                    "panStatus": "Duplicate",
                    "message": "This PAN is already used in the system.",
                },
            }
        elif api_name == "provide_zoom_link_non_individual":
            response = {
                "status": "success",
                "data": {
                    "zoomMeetingID": "356-339-3420",
                    "meetingPasscode": "Mosl@123",
                    "message": "Zoom link for Non-Individual account verification.",
                },
            }
        elif api_name == "checklist_for_individual":
            response = {
                "status": "success",
                "data": {
                    "checklistPath": "CBOS-2.0 > Customer Services > Circulars & Info",
                    "message": "Checklist details for an Individual account.",
                },
            }
        elif api_name == "checklist_for_non_individual":
            response = {
                "status": "success",
                "data": {
                    "checklistPath": "CBOS-2.0 > Customer Services > Circulars & Info",
                    "message": "Checklist details for a Non-Individual account.",
                },
            }
        elif api_name == "why_acop_form_rejected":
            response = {
                "status": "success",
                "data": {
                    "rejectionReason": "Issues found during Audit/SEBI inspection.",
                    "message": "Please rectify the objections and resend.",
                },
            }
        elif api_name == "kyc_non_compliance_clarification":
            response = {
                "status": "success",
                "data": {
                    "objectionDetail": "KYC incomplete. Pan/Address mismatch.",
                    "message": "Please update KYC documents.",
                },
            }
        elif api_name == "ipv_not_found":
            response = {
                "status": "success",
                "data": {
                    "ipvFound": False,
                    "message": "No matching IPV record in the system.",
                },
            }
        elif api_name == "email_mobile_validation_link":
            response = {
                "status": "success",
                "data": {
                    "linkDispatched": True,
                    "message": "Validation link sent to the provided email/mobile.",
                },
            }
        elif api_name == "segment_activation_status":
            response = {
                "status": "success",
                "data": {
                    "activatedSegments": ["Equity", "FNO"],
                    "message": "Segment activation successfully retrieved.",
                },
            }
        elif api_name == "where_to_check_sample_form":
            response = {
                "status": "success",
                "data": {
                    "pathInfo": "CBOS-2.0-2.0 > Customer Services > Circulars & Info",
                    "message": "Sample forms available under Circulars & Info.",
                },
            }
        elif api_name == "code_blocked_iaa":
            response = {
                "status": "success",
                "data": {
                    "blockedReason": "Awaiting KYC compliance documents.",
                    "message": "Please submit the required documents.",
                },
            }
        elif api_name == "nri_dormant_activation":
            abroad_docs = [
                "KRA page",
                "PAN/Passport with overseas verification (bank/notary/Embassy)",
            ]
            india_docs = [
                "KRA page with IPV",
                "PAN/Passport self-attested",
                "Latest immigration copy",
            ]
            response = {
                "status": "success",
                "data": {
                    "documentsRequired": (
                        abroad_docs if api_args.get("location") == "abroad" else india_docs
                    ),
                    "message": "Dormant reactivation instructions for NRI.",
                },
            }
        elif api_name == "dormant_status_online":
            response = {
                "status": "success",
                "data": {
                    "dormantStatus": "Pending",
                    "message": "Online reactivation request is under process.",
                },
            }
        elif api_name == "dormant_status_offline":
            response = {
                "status": "success",
                "data": {
                    "reactivationProgress": "In progress",
                    "message": "Offline dormant reactivation request is being processed.",
                },
            }
        elif api_name == "check_objection_new_account":
            response = {
                "status": "success",
                "data": {
                    "currentObjection": "Missing signature on KYC form.",
                    "message": "Please update the form with correct signature.",
                },
            }
        elif api_name == "check_objection_modification":
            response = {
                "status": "success",
                "data": {
                    "currentObjection": "Income proof mismatch.",
                    "message": "Please attach the correct income proof.",
                },
            }
        elif api_name == "clear_objection_new_account":
            response = {
                "status": "success",
                "data": {
                    "objectionCleared": True,
                    "message": "Objection for new account has been cleared.",
                },
            }
        elif api_name == "clear_objection_modification":
            response = {
                "status": "success",
                "data": {
                    "objectionCleared": True,
                    "message": "Modification objection resolved.",
                },
            }
        elif api_name == "clear_objection_closure":
            response = {
                "status": "success",
                "data": {"objectionCleared": True, "message": "Closure objection cleared."},
            }
        elif api_name == "what_is_my_objection":
            response = {
                "status": "success",
                "data": {
                    "objectionDetail": "KYC form not signed on last page.",
                    "message": "Please provide that signature.",
                },
            }
        elif api_name == "why_objection_raised":
            response = {
                "status": "success",
                "data": {
                    "causeOfObjection": "PAN mismatch with documents.",
                    "message": "Update correct PAN copy.",
                },
            }
        elif api_name == "cvl_kra_valid_but_iaa":
            response = {
                "status": "success",
                "data": {
                    "activationPendingReason": "Address mismatch still pending verification.",
                    "message": "Complete address verification to activate.",
                },
            }
        elif api_name == "why_dp_freeze":
            response = {
                "status": "success",
                "data": {
                    "freezeReason": "6-KYC attributes incomplete.",
                    "message": "Update all attributes to unfreeze.",
                },
            }
        elif api_name == "why_ac_suspended_iaa":
            response = {
                "status": "success",
                "data": {
                    "suspensionReason": "KYC Non-Compliance (IAA).",
                    "message": "Kindly submit KYC docs.",
                },
            }
        elif api_name == "kra_validated_but_cannot_trade":

            response = {
                "status": "success",
                "data": {
                    "canTrade": False,
                    "message": "KRA is valid, but system updates are still pending.",
                },
            }
        elif api_name == "kra_validation_failure":
            response = {
                "status": "success",
                "data": {
                    "validationLink": "https://validate.cvlindia.com/CVLKRAVerification_V1",
                    "message": "Please re-validate license by providing correct credentials.",
                },
            }
        elif api_name == "invalid_pan":
            response = {
                "status": "success",
                "data": {
                    "panValid": False,
                    "message": "Invalid or mismatched PAN details.",
                },
            }
        elif api_name == "segment_status_check":
            response = {
                "status": "success",
                "data": {
                    "activationDetails": ["Equity Activated", "F&O Pending"],
                    "message": "Detailed updates on each segment's status.",
                },
            }
        elif api_name == "why_new_ac_tba":
            response = {
                "status": "success",
                "data": {
                    "remainingSteps": "Awaiting final KRA check",
                    "message": "New account is pending activation.",
                },
            }
        elif api_name == "why_account_status_iaa":
            response = {
                "status": "success",
                "data": {
                    "suspensionCause": "Incomplete KYC attributes",
                    "message": "Complete missing KYC details.",
                },
            }
        elif api_name == "when_will_activate":
            response = {
                "status": "success",
                "data": {
                    "activationETA": "T+2 working days",
                    "message": "Account will be activated after final checks.",
                },
            }
        elif api_name == "why_dp_activation_pending":
            response = {
                "status": "success",
                "data": {
                    "pendingReason": "CVL KRA sync not completed",
                    "message": "Please allow some time for synchronization.",
                },
            }
        elif api_name == "why_validation_error":
            response = {
                "status": "success",
                "data": {
                    "errorDetails": "System mismatch with KRA data",
                    "message": "Please verify KRA details and re-try.",
                },
            }
        elif api_name == "dispatch_details_not_showing":
            response = {
                "status": "success",
                "data": {
                    "foundDispatch": False,
                    "message": "No courier record found in the system.",
                },
            }
        elif api_name == "courier_received_confirmation":
            response = {
                "status": "success",
                "data": {
                    "courierReceived": True,
                    "message": "Your courier has reached the Head Office.",
                },
            }
        elif api_name == "courier_dispatched_not_ack":
            response = {
                "status": "success",
                "data": {
                    "acknowledged": False,
                    "message": "Courier sent but not yet acknowledged.",
                },
            }
        elif api_name == "code_not_reflecting_in_dispatch":
            response = {
                "status": "success",
                "data": {
                    "isCodeListed": False,
                    "message": "The code was not found in courier dispatch records.",
                },
            }
        elif api_name == "why_ekyc_ac_tba":
            response = {
                "status": "success",
                "data": {
                    "activationPendingReason": "Aadhaar-based eSign in progress",
                    "message": "Please wait for final eSign confirmation.",
                },
            }
        elif api_name == "single_holder_rejected_to_ekyc":
            response = {
                "status": "success",
                "data": {
                    "requiredProcess": "EKYC",
                    "message": "Single-holder account must come through eKYC.",
                },
            }
        elif api_name == "not_able_to_request_kyc_form":
            response = {
                "status": "success",
                "data": {
                    "formAccess": False,
                    "message": "No direct request route found in CBOS 2.0. Contact support.",
                },
            }
        elif api_name == "i_want_my_acop_form":
            response = {
                "status": "success",
                "data": {
                    "acopFormLink": "Client Dashboard -> Quick Links -> KYC Document",
                    "message": "ACOP form has been retrieved for reference.",
                },
            }
        elif api_name == "where_check_kyc_scan":
            response = {
                "status": "success",
                "data": {
                    "kycScanAvailable": True,
                    "scanPath": "Client Dashboard -> Client Profile -> Quick links -> KYC document",
                    "message": "KYC scan is accessible via the dashboard.",
                },
            }
        else:
            response = {
                "status": "error",
                "message": "Unrecognized api_name. Please refer to the documentation.",
            }

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response)

        return response

class Account_opening_api_callerTool(BaseTool):
    name: str = "account_opening_api_caller"
    description: str = """The api_caller function handles all scenarios that need an API according to
your dataset. You can call this function with a specific api_name and any
relevant api_args (if required for that scenario). It then returns a JSON
object describing the result or data for that operation.

Below is the list of recognized api_name values, along with a brief
description of what each does, possible api_args, and what the return
JSON looks like.

1) "lead_not_found_in_saathi"
   ----------------------------------------------------
   Description:
     Checks if a lead exists in the Saathi system for a given client code
     and returns information about the lead status.
   Expected api_args:
     {
       "client_code": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "leadFound": bool,
         "message": str
       }
     }

2) "why_pan_already_exists"
   ----------------------------------------------------
   Description:
     Verifies if a given PAN is already present in the system.
   Expected api_args:
     {
       "pan_number": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "panStatus": "Duplicate" or "Unique",
         "message": str
       }
     }

3) "provide_zoom_link_non_individual"
   ----------------------------------------------------
   Description:
     Retrieves Zoom link details for non-individual account opening.
   Expected api_args: {}
   Return (example):
     {
       "status": "success",
       "data": {
         "zoomMeetingID": str,
         "meetingPasscode": str,
         "message": str
       }
     }

4) "checklist_for_individual"
   ----------------------------------------------------
   Description:
     Returns information on where to locate the checklist or form
     for opening an individual account.
   Expected api_args: {}
   Return (example):
     {
       "status": "success",
       "data": {
         "checklistPath": str,
         "message": str
       }
     }

5) "checklist_for_non_individual"
   ----------------------------------------------------
   Description:
     Returns details on where to locate the checklist or form
     for non-individual account opening.
   Expected api_args: {}
   Return (example):
     {
       "status": "success",
       "data": {
         "checklistPath": str,
         "message": str
       }
     }

6) "why_acop_form_rejected"
   ----------------------------------------------------
   Description:
     Fetches reasons why an ACOP physical form was rejected
     in the audit/inspection process.
   Expected api_args:
     {
       "client_code": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "rejectionReason": str,
         "message": str
       }
     }

7) "kyc_non_compliance_clarification"
   ----------------------------------------------------
   Description:
     Looks up the reasons for a KYC non-compliance objection.
   Expected api_args:
     {
       "client_code": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "objectionDetail": str,
         "message": str
       }
     }

8) "ipv_not_found"
   ----------------------------------------------------
   Description:
     Checks if an IPV code or name is present.
   Expected api_args:
     {
       "ipv_code": str,
       "ipv_name": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "ipvFound": bool,
         "message": str
       }
     }

9) "email_mobile_validation_link"
   ----------------------------------------------------
   Description:
     Validates whether an email/mobile verification link was sent.
   Expected api_args:
     {
       "client_code": str,
       "email": str,
       "mobile": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "linkDispatched": bool,
         "message": str
       }
     }

10) "segment_activation_status"
   ----------------------------------------------------
   Description:
     Retrieves the status of segment activation for a given client code.
   Expected api_args:
     {
       "client_code": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "activatedSegments": [str],
         "message": str
       }
     }

11) "where_to_check_sample_form"
   ----------------------------------------------------
   Description:
     Returns directions for where to locate a sample form.
   Expected api_args: {}
   Return (example):
     {
       "status": "success",
       "data": {
         "pathInfo": str,
         "message": str
       }
     }

12) "code_blocked_iaa"
   ----------------------------------------------------
   Description:
     Checks details if a code is blocked for IAA despite KRA being validated.
   Expected api_args:
     {
       "client_code": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "blockedReason": str,
         "message": str
       }
     }

13) "nri_dormant_activation"
   ----------------------------------------------------
   Description:
     Retrieves instructions or status for reactivating a dormant NRI account.
   Expected api_args:
     {
       "client_code": str,
       "location": "abroad" or "india"
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "documentsRequired": [str],
         "message": str
       }
     }

14) "dormant_status_online"
   ----------------------------------------------------
   Description:
     Checks the status of a dormant account reactivation request placed online.
   Expected api_args:
     {
       "client_code": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "dormantStatus": "Active" or "Pending",
         "message": str
       }
     }

15) "dormant_status_offline"
   ----------------------------------------------------
   Description:
     Checks the status of a dormant reactivation request placed offline.
   Expected api_args:
     {
       "sr_number": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "reactivationProgress": str,
         "message": str
       }
     }

16) "check_objection_new_account"
   ----------------------------------------------------
   Description:
     Looks up objection details for a new account application.
   Expected api_args:
     {
       "client_code": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "currentObjection": str,
         "message": str
       }
     }

17) "check_objection_modification"
   ----------------------------------------------------
   Description:
     Looks up objection details for a modification request.
   Expected api_args:
     {
       "client_code": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "currentObjection": str,
         "message": str
       }
     }

18) "clear_objection_new_account"
   ----------------------------------------------------
   Description:
     Indicates the steps taken to clear an objection raised for a new account.
   Expected api_args:
     {
       "client_code": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "objectionCleared": bool,
         "message": str
       }
     }

19) "clear_objection_modification"
   ----------------------------------------------------
   Description:
     Indicates how an objection for a modification was cleared.
   Expected api_args:
     {
       "client_code": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "objectionCleared": bool,
         "message": str
       }
     }

20) "clear_objection_closure"
   ----------------------------------------------------
   Description:
     States how an objection for a closure request was resolved.
   Expected api_args:
     {
       "client_code": str
     }
   Return (example):
     {
       "status": "success",
       "data": {
         "objectionCleared": bool,
         "message": str
       }
     }

21) "what_is_my_objection"
   ----------------------------------------------------
   Description:
     Retrieves a direct objection description tied to a client code.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "objectionDetail": str,
         "message": str
       }
     }

22) "why_objection_raised"
   ----------------------------------------------------
   Description:
     Explains the cause for an objection that has been raised.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "causeOfObjection": str,
         "message": str
       }
     }

23) "cvl_kra_valid_but_iaa"
   ----------------------------------------------------
   Description:
     Checks if CVL KRA is valid but the account is still in IAA status.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "activationPendingReason": str,
         "message": str
       }
     }

24) "why_dp_freeze"
   ----------------------------------------------------
   Description:
     Retrieves the reason a DP is frozen for a given client code.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "freezeReason": str,
         "message": str
       }
     }

25) "why_ac_suspended_iaa"
   ----------------------------------------------------
   Description:
     Provides reasons why an account is suspended due to IAA/KYC non-compliance.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "suspensionReason": str,
         "message": str
       }
     }

26) "kra_validated_but_cannot_trade"
   ----------------------------------------------------
   Description:
     Checks if KRA is validated but the client still cannot trade, possibly
     awaiting system updates or RMS checks.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "canTrade": bool,
         "message": str
       }
     }

27) "kra_validation_failure"
   ----------------------------------------------------
   Description:
     Provides instructions or status about a failed KRA validation.
   Expected api_args:
     {
       "pan_number": str,
       "mobile": str,
       "email": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "validationLink": str,
         "message": str
       }
     }

28) "invalid_pan"
   ----------------------------------------------------
   Description:
     Explains or checks if the provided PAN is invalid in the system.
   Expected api_args:
     {
       "pan_number": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "panValid": bool,
         "message": str
       }
     }

29) "segment_status_check"
   ----------------------------------------------------
   Description:
     Another way to see how segment activation is proceeding or completed.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "activationDetails": [str],
         "message": str
       }
     }

30) "why_new_ac_tba"
   ----------------------------------------------------
   Description:
     Reveals why a new account is showing as TBA (to be activated).
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "remainingSteps": str,
         "message": str
       }
     }

31) "why_account_status_iaa"
   ----------------------------------------------------
   Description:
     Clarifies why an account status is IAA while DP status is not frozen.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "suspensionCause": str,
         "message": str
       }
     }

32) "when_will_activate"
   ----------------------------------------------------
   Description:
     Tells how much time is left until the account is activated.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "activationETA": str,
         "message": str
       }
     }

33) "why_dp_activation_pending"
   ----------------------------------------------------
   Description:
     Returns the reason why DP activation is still pending for an account.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "pendingReason": str,
         "message": str
       }
     }

34) "why_validation_error"
   ----------------------------------------------------
   Description:
     Investigates a validation error the user may be seeing
     during or after account activation.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "errorDetails": str,
         "message": str
       }
     }

35) "dispatch_details_not_showing"
   ----------------------------------------------------
   Description:
     Checks why dispatch details for a courier are not visible in CBOS 2.0.
   Expected api_args:
     {
       "client_code": str,
       "dispatchType": str  # e.g., "ACOP", "MODIFICATION", "CLOSURE"
     }
   Return:
     {
       "status": "success",
       "data": {
         "foundDispatch": bool,
         "message": str
       }
     }

37) "courier_received_confirmation"
   ----------------------------------------------------
   Description:
     Confirms whether a courier was received at the HO.
   Expected api_args:
     {
       "packet_number": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "courierReceived": bool,
         "message": str
       }
     }

38) "courier_dispatched_not_ack"
   ----------------------------------------------------
   Description:
     Checks if a dispatched courier is still awaiting acknowledgement.
   Expected api_args:
     {
       "packet_number": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "acknowledged": bool,
         "message": str
       }
     }

39) "code_not_reflecting_in_dispatch"
   ----------------------------------------------------
   Description:
     Checks why a particular code does not show in courier dispatch records.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "isCodeListed": bool,
         "message": str
       }
     }

40) "why_ekyc_ac_tba"
   ----------------------------------------------------
   Description:
     Explains why an eKYC-based account is still at TBA status.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "activationPendingReason": str,
         "message": str
       }
     }

41) "single_holder_rejected_to_ekyc"
   ----------------------------------------------------
   Description:
     Indicates that single-holder accounts must use eKYC, clarifies
     why CBOS punching was rejected.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "requiredProcess": "EKYC",
         "message": str
       }
     }

42) "not_able_to_request_kyc_form"
   ----------------------------------------------------
   Description:
     Explains or processes requests for a KYC form if the user cannot request it
     from CBOS 2.0.
   Expected api_args:
     {
       "form_type": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "formAccess": bool,
         "message": str
       }
     }

43) "i_want_my_acop_form"
   ----------------------------------------------------
   Description:
     Retrieves the ACOP form or the path to it, often from the
     client dashboard.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "acopFormLink": str,
         "message": str
       }
     }

44) "where_check_kyc_scan"
   ----------------------------------------------------
   Description:
     Informs where a user can find or view the KYC scan associated
     with their account.
   Expected api_args:
     {
       "client_code": str
     }
   Return:
     {
       "status": "success",
       "data": {
         "kycScanAvailable": bool,
         "scanPath": str,
         "message": str
       }
     }"""
    args_schema: Type[BaseModel] = Account_opening_api_callerInput
    

    def _run(self, api_name: str, api_args: Optional[dict]=None, run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        print(api_name)
        if self.metadata is None:
            raise ValueError("Metadata is not provided")
        return account_opening_api_caller(api_name, api_args, self.metadata.get("record_api_call", None))

    async def _arun(self, api_name: str, api_args: Optional[dict] = None, run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
            raise ValueError("Metadata is not provided")
        return account_opening_api_caller(api_name, api_args, self.metadata.get("record_api_call", None))

class Banking_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: dict = Field(default={}, description='Argument api_args')

def banking_api_caller(api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None) -> dict:
        """
        Description:
            This function simulates API calls for various banking-related operations at Motilal Oswal.
            Each operation is identified by the 'api_name' parameter, and additional inputs
            can be passed through 'api_args'. Based on the 'api_name', the function returns
            a JSON object containing either status information, transaction details, or
            a message indicating the reason for any specific condition (e.g., rejection, pending status).

        Parameters:
            api_name (str):
                Indicates which API operation to perform. The supported operations are:
                    1. check_payout_status_yesterday
                    2. get_utr_ref_details
                    3. check_fund_transfer_status
                    4. get_payout_rejection_reason
                    5. check_cms_fund_transfer_status
                    6. check_razorpay_collection_status
                    7. fetch_third_party_transaction_details
                    8. check_ecms_fund_transfer_status
                    9. ba_brokerage_payout_rejected_reason
                    10. ba_partial_brokerage_payout
                    11. ba_sufficient_ledger_but_payout_rejected

            api_args (Optional[Dict]):
                A dictionary holding any arguments or details needed for the selected operation.
                Content and structure may vary depending on the ‘api_name’ in use. Some examples:
                    - client_code: str
                    - date_range: Dict (e.g., {"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"})
                    - sub_broker_code: str
                    - bank_details: Dict
                    - reason_code: str
                    - etc.

        Returns:
            Dict:
                A JSON-like dictionary consisting of:
                    - status: str (e.g., "success", "failed", "pending")
                    - message: str (detailed information or explanation)
                    - data: Dict (key-value pairs with any additional data,
                                  such as transaction details, UTRs, or relevant status codes)

        Usage:
            response = api_caller("check_payout_status_yesterday", {"client_code": "XYZ123"})
            print(response)
        """

        if api_name == "check_payout_status_yesterday":
            # scenario_id=533
            response_data = {
                "status": "success",
                "message": "Payout status retrieved successfully.",
                "data": {
                    "client_code": api_args.get("client_code", ""),
                    "payout_date": api_args.get("payout_date", ""),
                    "status_info": "Payout not received; processed next working day since it was raised after 5 PM.",
                },
            }

        elif api_name == "get_utr_ref_details":
            # scenario_id=534
            response_data = {
                "status": "success",
                "message": "UTR / reference number details fetched.",
                "data": {
                    "client_code": api_args.get("client_code", ""),
                    "date": api_args.get("date", ""),
                    "utr_number": "UTR123456TEST",
                    "reference_number": "REF987654",
                },
            }

        elif api_name == "check_fund_transfer_status":
            # scenario_id=539
            response_data = {
                "status": "success",
                "message": "Fund transfer details fetched.",
                "data": {
                    "client_code": api_args.get("client_code", ""),
                    "transfer_id": api_args.get("transfer_id", ""),
                    "transfer_status": "Rejected / Successful / Pending",
                    "reason": "Insufficient Balance / Other",
                },
            }

        elif api_name == "get_payout_rejection_reason":
            # scenario_id=540
            response_data = {
                "status": "success",
                "message": "Payout rejection reason retrieved.",
                "data": {
                    "client_code": api_args.get("client_code", ""),
                    "payout_date": api_args.get("payout_date", ""),
                    "rejection_reason": "Incorrect bank details / Mismatch in account details / Limits not met",
                },
            }

        elif api_name == "check_cms_fund_transfer_status":
            # scenario_id=542
            response_data = {
                "status": "success",
                "message": "CMS fund transfer status retrieved.",
                "data": {
                    "client_code": api_args.get("client_code", ""),
                    "cms_transfer_date": api_args.get("date", ""),
                    "cms_transfer_status": "Completed / Pending / Rejected",
                    "additional_info": "View or download from the Fund Transfer Report.",
                },
            }

        elif api_name == "check_razorpay_collection_status":
            # scenario_id=543
            response_data = {
                "status": "success",
                "message": "Razor Pay collection status obtained.",
                "data": {
                    "client_code": api_args.get("client_code", ""),
                    "transfer_type": "Razor pay Collection",
                    "transfer_date": api_args.get("date", ""),
                    "status_info": "Completed / Pending / Rejected",
                },
            }

        elif api_name == "fetch_third_party_transaction_details":
            # scenario_id=546
            response_data = {
                "status": "success",
                "message": "Third-party transaction details retrieved.",
                "data": {
                    "client_code": api_args.get("client_code", ""),
                    "transaction_id": api_args.get("transaction_id", ""),
                    "transaction_mark": "Third Party if from unmapped bank account",
                    "refund_status": "Initiated if bank proof not provided",
                },
            }

        elif api_name == "check_ecms_fund_transfer_status":
            # scenario_id=577
            response_data = {
                "status": "success",
                "message": "ECMS Fund Transfer status retrieved.",
                "data": {
                    "client_code": api_args.get("client_code", ""),
                    "transfer_date": api_args.get("date", ""),
                    "transfer_status": "Completed / Pending / Rejected",
                    "ecms_reference": "ECMS123456",
                },
            }

        elif api_name == "ba_brokerage_payout_rejected_reason":
            # scenario_id=882
            response_data = {
                "status": "failed",
                "message": "Brokerage payout rejected due to deposit shortfall or uncovered client debit in Risk Lab.",
                "data": {
                    "ba_code": api_args.get("ba_code", ""),
                    "check_channel_in_risk_lab": True,
                    "required_deposit_status": "Shortfall",
                    "recovery_action": "Please maintain required deposit or clear client debit.",
                },
            }

        elif api_name == "ba_partial_brokerage_payout":
            # scenario_id=884
            response_data = {
                "status": "partial",
                "message": "Partial brokerage payout released as deposit criteria not fully met.",
                "data": {
                    "ba_code": api_args.get("ba_code", ""),
                    "amount_released": api_args.get("partial_amount", 0),
                    "blocked_amount": api_args.get("blocked_amount", 0),
                    "uncovered_debit_reason": "Client debit remains uncovered. Check Risk Lab.",
                },
            }

        elif api_name == "ba_sufficient_ledger_but_payout_rejected":
            # scenario_id=890
            response_data = {
                "status": "failed",
                "message": "Payout request rejected despite sufficient ledger balance due to one or more constraints.",
                "data": {
                    "ba_code": api_args.get("ba_code", ""),
                    "constraints": [
                        "Open positions",
                        "50:50 criteria not maintained",
                        "Option writing block",
                        "Funds blocked under IAP or other reason",
                    ],
                    "next_step": "Kindly address the flagged items in Risk Lab and re-initiate the request.",
                },
            }

        else:
            # Fallback for any unknown API name
            response_data = {
                "status": "failed",
                "message": "Unknown API name or not supported by the current system.",
                "data": {},
            }

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response_data)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response_data)

        return response_data

class Banking_api_callerTool(BaseTool):
    name: str = "banking_api_caller"
    description: str = """Description:
    This function simulates API calls for various banking-related operations at Motilal Oswal.
    Each operation is identified by the 'api_name' parameter, and additional inputs
    can be passed through 'api_args'. Based on the 'api_name', the function returns
    a JSON object containing either status information, transaction details, or
    a message indicating the reason for any specific condition (e.g., rejection, pending status).

Parameters:
    api_name (str):
        Indicates which API operation to perform. The supported operations are:
            1. check_payout_status_yesterday
            2. get_utr_ref_details
            3. check_fund_transfer_status
            4. get_payout_rejection_reason
            5. check_cms_fund_transfer_status
            6. check_razorpay_collection_status
            7. fetch_third_party_transaction_details
            8. check_ecms_fund_transfer_status
            9. ba_brokerage_payout_rejected_reason
            10. ba_partial_brokerage_payout
            11. ba_sufficient_ledger_but_payout_rejected

    api_args (Optional[Dict]):
        A dictionary holding any arguments or details needed for the selected operation.
        Content and structure may vary depending on the ‘api_name’ in use. Some examples:
            - client_code: str
            - date_range: Dict (e.g., {"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"})
            - sub_broker_code: str
            - bank_details: Dict
            - reason_code: str
            - etc.

Returns:
    Dict:
        A JSON-like dictionary consisting of:
            - status: str (e.g., "success", "failed", "pending")
            - message: str (detailed information or explanation)
            - data: Dict (key-value pairs with any additional data,
                          such as transaction details, UTRs, or relevant status codes)

Usage:
    response = api_caller("check_payout_status_yesterday", {"client_code": "XYZ123"})
    print(response)"""
    args_schema: Type[BaseModel] = Banking_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return banking_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return banking_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

class Bo_franchise_signoff_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: Dict = Field(default={}, description='Argument api_args')

def bo_franchise_signoff_api_caller(
        api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None
    ) -> dict:
        """
        This function serves as a unified API caller to handle various operations
        that replicate the functionality provided by the CBOS tool in the Motilal Oswal
        Financial Services environment. The function bridges multiple scenarios related
        to franchise (BA) registration, NISM certificate handling, CTCL ID activation
        or deactivation, and BA profile updates (mobile number, email ID, address, etc.).

        PARAMETERS:
        ----------
        1) api_name (str):
           - Name of the specific API endpoint or operation to be performed.
           - Possible values include:

             a) "getFranchiseeRegistrationStatus"
                - Retrieves the status of franchisee registration.
                - Expected api_args keys:
                      {"ba_code": str (BA code or relevant identifier)}
                - Returns JSON structure:
                      {
                          "registration_status": str,   # e.g. "Active", "Pending"
                          "ba_code": str,
                          "exchange_details": list,     # e.g. ["NSE", "BSE"]
                          "remarks": str
                      }

             b) "verifyNISMCertificateUpload"
                - Checks if an NISM certificate has been successfully uploaded.
                - Expected api_args keys:
                      {"certificate_number": str, "ba_code": str}
                - Returns JSON structure:
                      {
                          "upload_status": str,         # e.g. "Uploaded", "Not Found"
                          "certificate_number": str,
                          "ba_code": str,
                          "remarks": str
                      }

             c) "checkNISMCertificateValidity"
                - Retrieves the validity period (expiry) of an NISM certificate.
                - Expected api_args keys:
                      {"certificate_number": str, "ba_code": str}
                - Returns JSON structure:
                      {
                          "validity_upto": str,         # e.g. "YYYY-MM-DD"
                          "certificate_number": str,
                          "ba_code": str,
                          "remarks": str
                      }

             d) "verifyCTCLIDActivation"
                - Verifies if a CTCL ID has been activated in the system.
                - Expected api_args keys:
                      {"ctcl_id": str, "ba_code": str}
                - Returns JSON structure:
                      {
                          "activation_status": str,     # e.g. "Active", "Inactive"
                          "ctcl_id": str,
                          "ba_code": str,
                          "remarks": str
                      }

             e) "verifyCTCLIDDeactivation"
                - Checks if a CTCL ID has been deactivated in the system.
                - Expected api_args keys:
                      {"ctcl_id": str, "ba_code": str}
                - Returns JSON structure:
                      {
                          "deactivation_status": str,   # e.g. "Deactivated", "Still Active"
                          "ctcl_id": str,
                          "ba_code": str,
                          "remarks": str
                      }

             f)  "initiateMobileNumberChange"
                - Initiates or handles the mobile number change process for a BA code across exchanges.
                - Expected api_args keys:
                      {"ba_code": str, "new_mobile_number": str}
                - Returns JSON structure:
                      {
                          "change_initiated": bool,
                          "ba_code": str,
                          "new_mobile_number": str,
                          "remarks": str
                      }

             g)  "getMobileNumberChangeDocuments"
                - Retrieves the list or path of required documents for changing the mobile number under BA code.
                - Expected api_args keys:
                      {"ba_code": str (optional if needed)}
                - Returns JSON structure:
                      {
                          "document_list": list,
                          "remarks": str
                      }

             h)  "checkMobileNumberUpdateStatus"
                - Confirms whether the mobile number has been updated in both CBOS and the exchange.
                - Expected api_args keys:
                      {"ba_code": str}
                - Returns JSON structure:
                      {
                          "update_status": str,         # e.g. "Updated", "Pending"
                          "ba_code": str,
                          "remarks": str
                      }

             i)  "initiateEmailChange"
                - Initiates the process of changing the email ID for a BA code across exchanges.
                - Expected api_args keys:
                      {"ba_code": str, "new_email": str}
                - Returns JSON structure:
                      {
                          "change_initiated": bool,
                          "ba_code": str,
                          "new_email": str,
                          "remarks": str
                      }

             j)  "getEmailChangeDocuments"
                - Retrieves the required document list or path for changing the email ID under BA code.
                - Expected api_args keys:
                      {"ba_code": str (optional if needed)}
                - Returns JSON structure:
                      {
                          "document_list": list,
                          "remarks": str
                      }

             k)  "checkEmailUpdateStatus"
                - Confirms whether the email ID has been updated in both CBOS and the exchange.
                - Expected api_args keys:
                      {"ba_code": str}
                - Returns JSON structure:
                      {
                          "update_status": str,         # e.g. "Updated", "Pending"
                          "ba_code": str,
                          "remarks": str
                      }

             l)  "initiateAddressChange"
                - Initiates the process of changing the address for a BA code across exchanges.
                - Expected api_args keys:
                      {"ba_code": str, "new_address": str}
                - Returns JSON structure:
                      {
                          "change_initiated": bool,
                          "ba_code": str,
                          "new_address": str,
                          "remarks": str
                      }

             m) "getAddressChangeDocuments"
                - Retrieves the required documents or path for changing the address under BA code.
                - Expected api_args keys:
                      {"ba_code": str (optional if needed)}
                - Returns JSON structure:
                      {
                          "document_list": list,
                          "remarks": str
                      }

             n) "checkAddressUpdateStatus"
                - Confirms whether the address has been updated in both CBOS and the exchange.
                - Expected api_args keys:
                      {"ba_code": str}
                - Returns JSON structure:
                      {
                          "update_status": str,         # e.g. "Updated, Pending"
                          "ba_code": str,
                          "remarks": str
                      }

        2) api_args (Dict, optional):
           - Dictionary containing the arguments required by a particular API call.
           - The keys within api_args are specific to the chosen api_name (detailed above).

        RETURN:
        -------
        The function returns a Python dictionary (JSON-friendly format) with keys/values relevant
        to the specific operation requested by api_name. The contents of this return structure
        vary based on the operation but will always include any data required to fulfill and
        confirm the requested action.

        USAGE EXAMPLE:
        -------------
        result = api_caller(
            api_name="getFranchiseeRegistrationStatus",
            api_args={"ba_code": "BA12345"}
        )
        print(result)

        # Possible output:
        # {
        #   "registration_status": "Active",
        #   "ba_code": "BA12345",
        #   "exchange_details": ["NSE", "BSE"],
        #   "remarks": "Registration is successfully completed."
        # }
        """
        response_data = {}

        if api_name == "getFranchiseeRegistrationStatus":
            response_data = {
                "registration_status": "Active",
                "ba_code": api_args.get("ba_code", ""),
                "exchange_details": ["NSE", "BSE"],
                "remarks": "Registration is verified in the system.",
            }

        elif api_name == "verifyNISMCertificateUpload":
            response_data = {
                "upload_status": "Uploaded",
                "certificate_number": api_args.get("certificate_number", ""),
                "ba_code": api_args.get("ba_code", ""),
                "remarks": "Certificate upload found in the system.",
            }

        elif api_name == "checkNISMCertificateValidity":
            response_data = {
                "validity_upto": "2025-12-31",
                "certificate_number": api_args.get("certificate_number", ""),
                "ba_code": api_args.get("ba_code", ""),
                "remarks": "Certificate is valid until the specified date.",
            }

        elif api_name == "verifyCTCLIDActivation":
            response_data = {
                "activation_status": "Active",
                "ctcl_id": api_args.get("ctcl_id", ""),
                "ba_code": api_args.get("ba_code", ""),
                "remarks": "CTCL ID activation verified in the system.",
            }

        elif api_name == "verifyCTCLIDDeactivation":
            response_data = {
                "deactivation_status": "Deactivated",
                "ctcl_id": api_args.get("ctcl_id", ""),
                "ba_code": api_args.get("ba_code", ""),
                "remarks": "CTCL ID marked as deactivated in the system.",
            }

        elif api_name == "initiateMobileNumberChange":
            response_data = {
                "change_initiated": True,
                "ba_code": api_args.get("ba_code", ""),
                "new_mobile_number": api_args.get("new_mobile_number", ""),
                "remarks": "Process initiated for mobile number change.",
            }

        elif api_name == "getMobileNumberChangeDocuments":
            response_data = {
                "document_list": [
                    "Authorized Person Change Form",
                    "Signed Request Letter",
                    "Self-attested ID Proof",
                ],
                "remarks": "Below is the list of documents required for mobile number update.",
            }

        elif api_name == "checkMobileNumberUpdateStatus":
            response_data = {
                "update_status": "Updated",
                "ba_code": api_args.get("ba_code", ""),
                "remarks": "Mobile number has been updated in CBOS and the exchange.",
            }

        elif api_name == "initiateEmailChange":
            response_data = {
                "change_initiated": True,
                "ba_code": api_args.get("ba_code", ""),
                "new_email": api_args.get("new_email", ""),
                "remarks": "Process initiated for email ID change.",
            }

        elif api_name == "getEmailChangeDocuments":
            response_data = {
                "document_list": [
                    "Authorized Person Change Form",
                    "Signed Request Letter",
                    "Self-attested ID Proof",
                ],
                "remarks": "Documents required for email ID update.",
            }

        elif api_name == "checkEmailUpdateStatus":
            response_data = {
                "update_status": "Updated",
                "ba_code": api_args.get("ba_code", ""),
                "remarks": "Email ID has been updated in CBOS and the exchange.",
            }

        elif api_name == "initiateAddressChange":
            response_data = {
                "change_initiated": True,
                "ba_code": api_args.get("ba_code", ""),
                "new_address": api_args.get("new_address", ""),
                "remarks": "Process initiated for address change.",
            }

        elif api_name == "getAddressChangeDocuments":
            response_data = {
                "document_list": [
                    "Address Change Form",
                    "Signed Request Letter",
                    "Address Proof Document",
                ],
                "remarks": "Documents required for address update.",
            }

        elif api_name == "checkAddressUpdateStatus":
            response_data = {
                "update_status": "Updated",
                "ba_code": api_args.get("ba_code", ""),
                "remarks": "Address has been updated in CBOS and the exchange.",
            }

        else:
            response_data = {
                "error": "Invalid API name specified.",
                "remarks": "Please check the api_name and try again.",
            }

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response_data)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response_data)

        return response_data

class Bo_franchise_signoff_api_callerTool(BaseTool):
    name: str = "bo_franchise_signoff_api_caller"
    description: str = """This function serves as a unified API caller to handle various operations
that replicate the functionality provided by the CBOS tool in the Motilal Oswal
Financial Services environment. The function bridges multiple scenarios related
to franchise (BA) registration, NISM certificate handling, CTCL ID activation
or deactivation, and BA profile updates (mobile number, email ID, address, etc.).

PARAMETERS:
----------
1) api_name (str):
   - Name of the specific API endpoint or operation to be performed.
   - Possible values include:

     a) "getFranchiseeRegistrationStatus"
        - Retrieves the status of franchisee registration.
        - Expected api_args keys:
              {"ba_code": str (BA code or relevant identifier)}
        - Returns JSON structure:
              {
                  "registration_status": str,   # e.g. "Active", "Pending"
                  "ba_code": str,
                  "exchange_details": list,     # e.g. ["NSE", "BSE"]
                  "remarks": str
              }

     b) "verifyNISMCertificateUpload"
        - Checks if an NISM certificate has been successfully uploaded.
        - Expected api_args keys:
              {"certificate_number": str, "ba_code": str}
        - Returns JSON structure:
              {
                  "upload_status": str,         # e.g. "Uploaded", "Not Found"
                  "certificate_number": str,
                  "ba_code": str,
                  "remarks": str
              }

     c) "checkNISMCertificateValidity"
        - Retrieves the validity period (expiry) of an NISM certificate.
        - Expected api_args keys:
              {"certificate_number": str, "ba_code": str}
        - Returns JSON structure:
              {
                  "validity_upto": str,         # e.g. "YYYY-MM-DD"
                  "certificate_number": str,
                  "ba_code": str,
                  "remarks": str
              }

     d) "verifyCTCLIDActivation"
        - Verifies if a CTCL ID has been activated in the system.
        - Expected api_args keys:
              {"ctcl_id": str, "ba_code": str}
        - Returns JSON structure:
              {
                  "activation_status": str,     # e.g. "Active", "Inactive"
                  "ctcl_id": str,
                  "ba_code": str,
                  "remarks": str
              }

     e) "verifyCTCLIDDeactivation"
        - Checks if a CTCL ID has been deactivated in the system.
        - Expected api_args keys:
              {"ctcl_id": str, "ba_code": str}
        - Returns JSON structure:
              {
                  "deactivation_status": str,   # e.g. "Deactivated", "Still Active"
                  "ctcl_id": str,
                  "ba_code": str,
                  "remarks": str
              }

     f)  "initiateMobileNumberChange"
        - Initiates or handles the mobile number change process for a BA code across exchanges.
        - Expected api_args keys:
              {"ba_code": str, "new_mobile_number": str}
        - Returns JSON structure:
              {
                  "change_initiated": bool,
                  "ba_code": str,
                  "new_mobile_number": str,
                  "remarks": str
              }

     g)  "getMobileNumberChangeDocuments"
        - Retrieves the list or path of required documents for changing the mobile number under BA code.
        - Expected api_args keys:
              {"ba_code": str (optional if needed)}
        - Returns JSON structure:
              {
                  "document_list": list,
                  "remarks": str
              }

     h)  "checkMobileNumberUpdateStatus"
        - Confirms whether the mobile number has been updated in both CBOS and the exchange.
        - Expected api_args keys:
              {"ba_code": str}
        - Returns JSON structure:
              {
                  "update_status": str,         # e.g. "Updated", "Pending"
                  "ba_code": str,
                  "remarks": str
              }

     i)  "initiateEmailChange"
        - Initiates the process of changing the email ID for a BA code across exchanges.
        - Expected api_args keys:
              {"ba_code": str, "new_email": str}
        - Returns JSON structure:
              {
                  "change_initiated": bool,
                  "ba_code": str,
                  "new_email": str,
                  "remarks": str
              }

     j)  "getEmailChangeDocuments"
        - Retrieves the required document list or path for changing the email ID under BA code.
        - Expected api_args keys:
              {"ba_code": str (optional if needed)}
        - Returns JSON structure:
              {
                  "document_list": list,
                  "remarks": str
              }

     k)  "checkEmailUpdateStatus"
        - Confirms whether the email ID has been updated in both CBOS and the exchange.
        - Expected api_args keys:
              {"ba_code": str}
        - Returns JSON structure:
              {
                  "update_status": str,         # e.g. "Updated", "Pending"
                  "ba_code": str,
                  "remarks": str
              }

     l)  "initiateAddressChange"
        - Initiates the process of changing the address for a BA code across exchanges.
        - Expected api_args keys:
              {"ba_code": str, "new_address": str}
        - Returns JSON structure:
              {
                  "change_initiated": bool,
                  "ba_code": str,
                  "new_address": str,
                  "remarks": str
              }

     m) "getAddressChangeDocuments"
        - Retrieves the required documents or path for changing the address under BA code.
        - Expected api_args keys:
              {"ba_code": str (optional if needed)}
        - Returns JSON structure:
              {
                  "document_list": list,
                  "remarks": str
              }

     n) "checkAddressUpdateStatus"
        - Confirms whether the address has been updated in both CBOS and the exchange.
        - Expected api_args keys:
              {"ba_code": str}
        - Returns JSON structure:
              {
                  "update_status": str,         # e.g. "Updated, Pending"
                  "ba_code": str,
                  "remarks": str
              }

2) api_args (Dict, optional):
   - Dictionary containing the arguments required by a particular API call.
   - The keys within api_args are specific to the chosen api_name (detailed above).

RETURN:
-------
The function returns a Python dictionary (JSON-friendly format) with keys/values relevant
to the specific operation requested by api_name. The contents of this return structure
vary based on the operation but will always include any data required to fulfill and
confirm the requested action.

USAGE EXAMPLE:
-------------
result = api_caller(
    api_name="getFranchiseeRegistrationStatus",
    api_args={"ba_code": "BA12345"}
)
print(result)

# Possible output:
# {
#   "registration_status": "Active",
#   "ba_code": "BA12345",
#   "exchange_details": ["NSE", "BSE"],
#   "remarks": "Registration is successfully completed."
# }"""
    args_schema: Type[BaseModel] = Bo_franchise_signoff_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return bo_franchise_signoff_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return bo_franchise_signoff_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

class Clarification_on_brokerage_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: Dict = Field(default={}, description='Argument api_args')

def clarification_on_brokerage_api_caller(
        api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None
    ) -> Dict:
        """
        The 'api_caller' function acts as a gateway to various internal APIs of the
        Motilal Oswal Financial Services (MO) CBOS system. Depending on the specified
        'api_name', it will execute an internal call to fetch or process brokerage-related
        information.

        Parameters:
        -----------
        api_name : str
            Name of the API operation to perform. The allowed values (based on
            the scenarios where an API is required) are:

            1) "get_brokerage_slab_all_segments"
                • Scenario ID: 263
                • Retrieves the brokerage slab for all segments of a given client.
                • api_args could include:
                    {
                      "client_id": str,
                      "include_history": bool (optional)
                    }
                • Returns brokerage slab details for the requested client.

            2) "get_revised_brokerage_slab_status"
                • Scenario ID: 264
                • Retrieves the status of any requested update or revision to the
                  brokerage slab.
                • api_args could include:
                    {
                      "client_id": str
                    }
                • Returns the current status or any ongoing changes to the brokerage slab.

            3) "get_brokerage_slab"
                • Scenario ID: 267
                • Retrieves brokerage slab when the client or BA cannot access the
                  Rise app or web portal.
                • api_args could include:
                    {
                      "client_id": str
                    }
                • Returns the brokerage details (equity delivery, intraday, futures, options).

            4) "get_options_brokerage_details"
                • Scenario ID: 269
                • Retrieves the brokerage details charged for Options trades.
                • api_args could include:
                    {
                      "client_id": str
                    }
                • Returns the settings or rates applied for Options brokerage.

            5) "get_equity_intraday_brokerage_report"
                • Scenario ID: 271
                • Provides a detailed breakdown of intraday equity brokerage charges
                  for one or more trades.
                • api_args could include:
                    {
                      "client_id": str,
                      "trade_date": str (format: "YYYY-MM-DD"),
                      "segment": str (e.g., "EQ")
                    }
                • Returns a report containing trade details and corresponding brokerage charges.

            6) "get_futures_brokerage_report"
                • Scenario ID: 272
                • Provides a breakdown of brokerage charges for Futures trades.
                • api_args could include:
                    {
                      "client_id": str,
                      "trade_date": str (format: "YYYY-MM-DD"),
                      "segment": str (e.g., "DR")
                    }
                • Returns a detailed list of futures trades and relevant brokerage charges.

        api_args : Dict, optional
            This dictionary contains all the necessary parameters for the specific
            API call. The exact keys depend on the 'api_name'. For example, if the
            'api_name' is "get_equity_intraday_brokerage_report", you might include
            "client_id" and "trade_date".

        Returns:
        --------
        Dict
            A JSON-compatible dictionary object providing two main keys:
              - "status": indicates the result of the call (e.g., "success", "error").
              - "data": the payload containing the requested details or a relevant
                message for the operation.

        Usage Flow:
        -----------
        The function looks at the 'api_name' and routes the request to the corresponding
        internal CBOS API. The 'api_args' are used to construct or filter the request
        within CBOS. After obtaining the result, the function assembles a JSON
        structure that includes "status" and "data" keys with the requested information.

        Example:
        --------
        response = api_caller(
            api_name="get_equity_intraday_brokerage_report",
            api_args={
                "client_id": "C12345",
                "trade_date": "2023-09-25",
                "segment": "EQ"
            }
        )
        print(response)
        # Expected output:
        # {
        #   "status": "success",
        #   "data": {
        #       "trades": [...],
        #       "brokerage_total": ...,
        #       ...
        #   }
        # }

        Notes:
        ------
        1. Error handling for invalid or missing arguments is not shown here, but in
           practice, you would want to verify the presence of required keys in 'api_args'.
        2. This function can be extended or modified for any additional scenarios or
           expansions in the MO CBOS system.
        """
        if api_args is None:
            api_args = {}

        response_payload = {}

        if api_name == "get_brokerage_slab_all_segments":
            # Scenario ID: 263
            # Implementation steps might include calling a brokerage slab endpoint in CBOS
            # to fetch the brokerage for all segments of this client.
            response_payload = {
                "status": "success",
                "data": {
                    "client_id": api_args.get("client_id", ""),
                    "brokerage_slab": "Brokerage slab details for all segments",
                    "include_history": api_args.get("include_history", False),
                },
            }

        elif api_name == "get_revised_brokerage_slab_status":
            # Scenario ID: 264
            # Retrieves the status of the requested brokerage slab update from CBOS.
            response_payload = {
                "status": "success",
                "data": {
                    "client_id": api_args.get("client_id", ""),
                    "revision_status": "Approved/Pending/Rejected",
                },
            }

        elif api_name == "get_brokerage_slab":
            # Scenario ID: 267
            # General brokerage slab fetch when a client or BA doesn't want to use the Rise app or web portal.
            response_payload = {
                "status": "success",
                "data": {
                    "client_id": api_args.get("client_id", ""),
                    "brokerage_details": {
                        "equity_delivery": "0.50%",
                        "equity_intraday": "0.05%",
                        "futures": "0.03%",
                        "options": "₹20 per lot",
                    },
                },
            }

        elif api_name == "get_options_brokerage_details":
            # Scenario ID: 269
            # High brokerage charged for Options -> fetch the client's Options brokerage details.
            response_payload = {
                "status": "success",
                "data": {
                    "client_id": api_args.get("client_id", ""),
                    "options_brokerage_slab": "₹20 per lot",
                    "notes": "Brokerage charged according to the assigned slab.",
                },
            }

        elif api_name == "get_equity_intraday_brokerage_report":
            # Scenario ID: 271
            # Provides clarity on intraday equity brokerage details for a client.
            response_payload = {
                "status": "success",
                "data": {
                    "client_id": api_args.get("client_id", ""),
                    "trade_date": api_args.get("trade_date", ""),
                    "segment": api_args.get("segment", "EQ"),
                    "trade_report": [
                        {
                            "symbol": "XYZ",
                            "quantity": 100,
                            "brokerage_charged": 10,
                            "time": "10:15 AM",
                        },
                        # additional trade entries...
                    ],
                },
            }

        elif api_name == "get_futures_brokerage_report":
            # Scenario ID: 272
            # Provides clarity on futures brokerage details, including charges and trades.
            response_payload = {
                "status": "success",
                "data": {
                    "client_id": api_args.get("client_id", ""),
                    "trade_date": api_args.get("trade_date", ""),
                    "segment": api_args.get("segment", "DR"),
                    "trade_report": [
                        {
                            "symbol": "ABC FUT",
                            "lots": 2,
                            "brokerage_charged": 50,
                            "time": "12:30 PM",
                        },
                        # additional trade entries...
                    ],
                },
            }

        else:
            # Handle unrecognized API names or scenario
            response_payload = {
                "status": "error",
                "data": {"message": f"Unknown api_name '{api_name}'"},
            }

          # api_tracker = APITracker.get_instance()
          # api_tracker.record_api_call(api_name, api_args, response_payload)
        if callable(record_api_call):
          record_api_call(api_name, api_args, response_payload)

        return response_payload

class Clarification_on_brokerage_api_callerTool(BaseTool):
    name: str = "clarification_on_brokerage_api_caller"
    description: str = """The 'api_caller' function acts as a gateway to various internal APIs of the
Motilal Oswal Financial Services (MO) CBOS system. Depending on the specified
'api_name', it will execute an internal call to fetch or process brokerage-related
information.

Parameters:
-----------
api_name : str
    Name of the API operation to perform. The allowed values (based on
    the scenarios where an API is required) are:

    1) "get_brokerage_slab_all_segments"
        • Scenario ID: 263
        • Retrieves the brokerage slab for all segments of a given client.
        • api_args could include:
            {
              "client_id": str,
              "include_history": bool (optional)
            }
        • Returns brokerage slab details for the requested client.

    2) "get_revised_brokerage_slab_status"
        • Scenario ID: 264
        • Retrieves the status of any requested update or revision to the
          brokerage slab.
        • api_args could include:
            {
              "client_id": str
            }
        • Returns the current status or any ongoing changes to the brokerage slab.

    3) "get_brokerage_slab"
        • Scenario ID: 267
        • Retrieves brokerage slab when the client or BA cannot access the
          Rise app or web portal.
        • api_args could include:
            {
              "client_id": str
            }
        • Returns the brokerage details (equity delivery, intraday, futures, options).

    4) "get_options_brokerage_details"
        • Scenario ID: 269
        • Retrieves the brokerage details charged for Options trades.
        • api_args could include:
            {
              "client_id": str
            }
        • Returns the settings or rates applied for Options brokerage.

    5) "get_equity_intraday_brokerage_report"
        • Scenario ID: 271
        • Provides a detailed breakdown of intraday equity brokerage charges
          for one or more trades.
        • api_args could include:
            {
              "client_id": str,
              "trade_date": str (format: "YYYY-MM-DD"),
              "segment": str (e.g., "EQ")
            }
        • Returns a report containing trade details and corresponding brokerage charges.

    6) "get_futures_brokerage_report"
        • Scenario ID: 272
        • Provides a breakdown of brokerage charges for Futures trades.
        • api_args could include:
            {
              "client_id": str,
              "trade_date": str (format: "YYYY-MM-DD"),
              "segment": str (e.g., "DR")
            }
        • Returns a detailed list of futures trades and relevant brokerage charges.

api_args : Dict, optional
    This dictionary contains all the necessary parameters for the specific
    API call. The exact keys depend on the 'api_name'. For example, if the
    'api_name' is "get_equity_intraday_brokerage_report", you might include
    "client_id" and "trade_date".

Returns:
--------
Dict
    A JSON-compatible dictionary object providing two main keys:
      - "status": indicates the result of the call (e.g., "success", "error").
      - "data": the payload containing the requested details or a relevant
        message for the operation.

Usage Flow:
-----------
The function looks at the 'api_name' and routes the request to the corresponding
internal CBOS API. The 'api_args' are used to construct or filter the request
within CBOS. After obtaining the result, the function assembles a JSON
structure that includes "status" and "data" keys with the requested information.

Example:
--------
response = api_caller(
    api_name="get_equity_intraday_brokerage_report",
    api_args={
        "client_id": "C12345",
        "trade_date": "2023-09-25",
        "segment": "EQ"
    }
)
print(response)
# Expected output:
# {
#   "status": "success",
#   "data": {
#       "trades": [...],
#       "brokerage_total": ...,
#       ...
#   }
# }

Notes:
------
1. Error handling for invalid or missing arguments is not shown here, but in
   practice, you would want to verify the presence of required keys in 'api_args'.
2. This function can be extended or modified for any additional scenarios or
   expansions in the MO CBOS system."""
    args_schema: Type[BaseModel] = Clarification_on_brokerage_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return clarification_on_brokerage_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return clarification_on_brokerage_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

class Compliance_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: dict = Field(default={}, description='Argument api_args')

def compliance_api_caller(api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None) -> dict:
        """
        This function serves as a single entry point for various operations that
        correspond to different scenario requirements. The specific operation to be
        performed is determined by the 'api_name' parameter.

        Parameters:
        -----------
        api_name : str
            Name of the API operation to be performed. Possible values include:
                - "get_circular_for_penalty_charges"
                - "download_interest_file"
                - "download_penalty_report"

        api_args : Optional[Dict], default = {}
            A dictionary of arguments required for the chosen operation.
            Example arguments may include:
                - scenario_id (int)
                - date_range (tuple)
                - other relevant filters

        Returns:
        --------
        Dict
            A JSON-like dictionary containing the information relevant to the API call.
            The structure of this dictionary varies based on the value of 'api_name'.

        Description of Operations:
        --------------------------
        1) get_circular_for_penalty_charges
           - Used to retrieve information about any circular available regarding penalty charges.
           - api_args could include scenario_id if needed.
           - The return value provides details about the circular, reference number, and instructions
             on how to access it.

        2) download_interest_file
           - Used to generate or retrieve interest file reports (for DPC interest).
           - The return value contains the steps to download the report, file name, or a
             URL reference, along with any additional metadata.

        3) download_penalty_report
           - Used to generate or retrieve penalty reports (penalty bifurcation).
           - The return value includes the path for the report download or relevant metadata.

        Usage Example:
        --------------
        response = api_caller("get_circular_for_penalty_charges", {"scenario_id": 772})
        """
        response_data = {}

        if api_name == "get_circular_for_penalty_charges":
            # Could optionally use api_args.get("scenario_id")
            response_data = {
                "circular_ref_no": "7226554",
                "information_path": "Customer Service > Circular and Info",
                "message": "Circular retrieved successfully.",
                "additional_info": "Circular is available for reference regarding penalty charges.",
            }

        elif api_name == "download_interest_file":
            # Could optionally use api_args.get("scenario_id")
            response_data = {
                "report_name": "DPC Interest Report",
                "download_path": "Banking & Ops > Reports > DPC Interest Report",
                "message": "Interest file generated and available for download.",
                "additional_info": "You can access the interest file through the specified path.",
            }

        elif api_name == "download_penalty_report":
            # Could optionally use api_args.get("scenario_id")
            response_data = {
                "report_name": "Penalty Bifurcation Report",
                "download_path": "Trading Reports > Penalty Bifurcation Report",
                "message": "Penalty report generated and available for download.",
                "additional_info": "You can access the penalty report through the specified path.",
            }
        else:
            response_data = {
                "error": "Invalid API name provided.",
                "available_apis": [
                    "get_circular_for_penalty_charges",
                    "download_interest_file",
                    "download_penalty_report",
                ],
            }

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response_data)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response_data)

        return response_data

class Compliance_api_callerTool(BaseTool):
    name: str = "compliance_api_caller"
    description: str = """This function serves as a single entry point for various operations that
correspond to different scenario requirements. The specific operation to be
performed is determined by the 'api_name' parameter.

Parameters:
-----------
api_name : str
    Name of the API operation to be performed. Possible values include:
        - "get_circular_for_penalty_charges"
        - "download_interest_file"
        - "download_penalty_report"

api_args : Optional[Dict], default = {}
    A dictionary of arguments required for the chosen operation.
    Example arguments may include:
        - scenario_id (int)
        - date_range (tuple)
        - other relevant filters

Returns:
--------
Dict
    A JSON-like dictionary containing the information relevant to the API call.
    The structure of this dictionary varies based on the value of 'api_name'.

Description of Operations:
--------------------------
1) get_circular_for_penalty_charges
   - Used to retrieve information about any circular available regarding penalty charges.
   - api_args could include scenario_id if needed.
   - The return value provides details about the circular, reference number, and instructions
     on how to access it.

2) download_interest_file
   - Used to generate or retrieve interest file reports (for DPC interest).
   - The return value contains the steps to download the report, file name, or a
     URL reference, along with any additional metadata.

3) download_penalty_report
   - Used to generate or retrieve penalty reports (penalty bifurcation).
   - The return value includes the path for the report download or relevant metadata.

Usage Example:
--------------
response = api_caller("get_circular_for_penalty_charges", {"scenario_id": 772})"""
    args_schema: Type[BaseModel] = Compliance_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return compliance_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return compliance_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

class Dp_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: dict = Field(default={}, description='Argument api_args')

def dp_api_caller(api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None) -> dict:
        """
        Description:
            The api_caller function is designed to handle and return data for various
            operational or support-related scenarios that require an API. The function
            takes in:

            1) api_name (str): A string specifying which scenario or operation to perform.
            2) api_args (dict): An optional dictionary of arguments that can be used
               for processing or filtering. Its usage may vary depending on the specific
               scenario.

            Return Value:
            A dictionary (JSON-like) containing:
              - scenario_id: Numeric identifier of the scenario.
              - scenario: A brief description of the situation or question.
              - path: The path or steps typically taken in a support tool (CBOS-2.0) or
                user portal to handle the request.
              - type_of_process: The type of the process (e.g., Status, Process, Technical).
              - additional fields or notes relevant to that scenario.

            Usage:
            This function centralizes all possible “api_required” scenarios so that
            a conversational or automation agent can retrieve the correct handling steps
            and references for each specific request. The structure may be expanded or
            replaced by real API integrations in the future.
        """

        # Scenario 102
        if api_name == "add_beneficiary_manually":
            response = {
                "scenario_id": 102,
                "scenario": "Add beneficiary manually",
                "path": "CBOS-2.0 >> DEPOSITORY >> Reports >> Beneficiary status report",
                "type_of_process": "Process",
            }

        # Scenario 104
        elif api_name == "unable_to_add_beneficiary":
            response = {
                "scenario_id": 104,
                "scenario": "Unable to add beneficiary",
                "path": "CBOS-2.0 >> Depository >> Reports >> Beneficiary status report",
                "type_of_process": "Technical",
            }

        # Scenario 105
        elif api_name == "is_beneficiary_added":
            response = {
                "scenario_id": 105,
                "scenario": "Is my beneficiary added",
                "path": "CBOS-2.0 >> DEPOSITORY >> REPORT >> BENEFICIARY REPORT",
                "type_of_process": "Status",
            }

        # Scenario 106
        elif api_name == "why_beneficiary_rejected":
            response = {
                "scenario_id": 106,
                "scenario": "Why is beneficiary getting rejected",
                "path": "CBOS-2.0 >> Depository >> Reports >> Beneficiary status report",
                "type_of_process": "Status",
            }

        # Scenario 107
        elif api_name == "how_to_add_beneficiary":
            response = {
                "scenario_id": 107,
                "scenario": "How to add beneficiary",
                "path": (
                    "1) CBOS-2.0 >> DEPOSITORY >> REQUEST >> ADD BENEFICARY \n"
                    "2) E-off market (Old version) >> Reports >> Demat holdings >> "
                    "E - off market >> ADD Beneficiary"
                ),
                "type_of_process": "Process",
            }

        # Scenario 108
        elif api_name == "check_beneficiary_details":
            response = {
                "scenario_id": 108,
                "scenario": "Where can I check my beneficiary added details",
                "path": (
                    "1) CBOS-2.0 >> DEPOSITORY >> REPORTS >> BENEFICIARY\n"
                    "2) E-off market (Old version) >> Reports >> Demat holdings >> E - off market >> Beneficiary report"
                ),
                "type_of_process": "Process",
            }

        # Scenario 109
        elif api_name == "beneficiary_active_but_dis_not_processing":
            response = {
                "scenario_id": 109,
                "scenario": "Beneficiary already active but unable to process DIS",
                "path": "CBOS-2.0 >> DEPOSITIRY >> Reports >> Beneficiary status report",
                "type_of_process": "Technical",
            }

        # Scenario 114
        elif api_name == "process_punched_dis":
            response = {
                "scenario_id": 114,
                "scenario": "Process the DIS which is punched",
                "path": "CBOS-2.0 >> DEPOSITORY >> REPORTS >> STATUS REPORT",
                "type_of_process": "Process",
            }

        # Scenario 115
        elif api_name == "why_is_dis_rejected":
            response = {
                "scenario_id": 115,
                "scenario": "Why is DIS rejected",
                "path": "CBOS-2.0 >> DEPOSITORY >> REPORTS >> STATUS REPORTS >>",
                "type_of_process": "Status",
            }

        # Scenario 116
        elif api_name == "dis_not_processed_yet":
            response = {
                "scenario_id": 116,
                "scenario": "DIS is not processed yet",
                "path": "CBOS-2.0 >> DEPOSITORY >> REPORTS >> STATUS REPORTS >>",
                "type_of_process": "Status",
            }

        # Scenario 117
        elif api_name == "dis_execution_completed_no_stocks":
            response = {
                "scenario_id": 117,
                "scenario": "DIS execution is completed but stocks are not yet credited",
                "path": "CBOS-2.0 >> DEPOSITORY >> REPORTS >> STATUS REPORTS >>",
                "type_of_process": "Status",
            }

        # Scenario 118
        elif api_name == "rejection_clarification_dis":
            response = {
                "scenario_id": 118,
                "scenario": "Rejection clarification",
                "path": "CBOS-2.0 >> DEPOSITORY >> REPORTS >> STATUS REPORTS >>",
                "type_of_process": "Status",
            }

        # Scenario 120
        elif api_name == "online_dis_option":
            response = {
                "scenario_id": 120,
                "scenario": "Is there any online DIS execution option (E Off market)?",
                "path": "E -OFF market (Old version) >>Reports >> Demat holdings >> E - off market",
                "type_of_process": "Process",
            }

        # Scenario 128
        elif api_name == "where_form_add_beneficiary":
            response = {
                "scenario_id": 128,
                "scenario": "Where is the form to add beneficiary, available?",
                "path": "CBOS-2.0 >> Depository >> Request >> ADD Beneficiary",
                "type_of_process": "Process",
            }

        # Scenario 129
        elif api_name == "undelivered_dis_book_returned":
            response = {
                "scenario_id": 129,
                "scenario": "What happens in case of undelivered DIS book that is returned to HO?",
                "path": "CBOS-2.0 >> DEPOSITIRY >> Reports >> Status report >> Slip requisition",
                "type_of_process": "Process",
            }

        # Scenario 139
        elif api_name == "dis_book_not_received":
            response = {
                "scenario_id": 139,
                "scenario": "Book not received yet.",
                "path": "CBOS-2.0 >> Depository >> Slip requisition",
                "type_of_process": "Status",
            }

        # Scenario 140
        elif api_name == "dis_book_returned_back":
            response = {
                "scenario_id": 140,
                "scenario": "Book returned back",
                "path": "N/A",
                "type_of_process": "Status",
            }

        # Scenario 157
        elif api_name == "transfer_shares_charges":
            response = {
                "scenario_id": 157,
                "scenario": "Are there any charges for transferring shares?",
                "path": "N/A",
                "type_of_process": "Process",
            }

        # Scenario 159
        elif api_name == "drf_current_status":
            response = {
                "scenario_id": 159,
                "scenario": "What is the DRF Current status",
                "path": "CBOS-2.0 >> Depository >> Reports >> Status",
                "type_of_process": "Status",
            }

        # Scenario 160
        elif api_name == "rejected_drf_not_returned_yet":
            response = {
                "scenario_id": 160,
                "scenario": "Rejected DRF not returned yet",
                "path": "CBOS-2.0 >> Depository >> Reports >> Status",
                "type_of_process": "Status",
            }

        # Scenario 162
        elif api_name == "drf_rejection_clarification":
            response = {
                "scenario_id": 162,
                "scenario": "Required rejection clarification (DRF)",
                "path": "CBOS-2.0 >> Depository >> Request >> DRF RRF Request >> Rejected DRF details",
                "type_of_process": "Status",
            }

        # Scenario 163
        elif api_name == "drf_processed_no_shares_credited":
            response = {
                "scenario_id": 163,
                "scenario": "DRF has been processed but shares not credited yet",
                "path": (
                    "CBOS-2.0 >> Depository >> Reports >> Status\n"
                    "CBOS-2.0 >> Depository >> Reports >> Holding cum transaction"
                ),
                "type_of_process": "Status",
            }

        # Scenario 166
        elif api_name == "convert_physical_to_demat":
            response = {
                "scenario_id": 166,
                "scenario": "What is required to convert physical shares in Demat",
                "path": "CBOS-2.0 >> Depository >> Request >> DRF RRF request >> Add new.",
                "type_of_process": "Process",
            }

        # Scenario 170
        elif api_name == "demat_processed_unable_to_sell":
            response = {
                "scenario_id": 170,
                "scenario": "Demat showing processed but unable to sell / view for selling",
                "path": (
                    "CBOS-2.0 >> Depository >> Reports >> Status\n"
                    "CBOS-2.0 >> Depository >> Reports >> Holding cum transaction"
                ),
                "type_of_process": "Process",
            }

        # Scenario 177
        elif api_name == "tat_sending_shares_to_rta":
            response = {
                "scenario_id": 177,
                "scenario": "What is the TAT for sending the shares to RTA for dematerialisation by DP?",
                "path": "N/A",
                "type_of_process": "Status",
            }

        # Scenario 188
        elif api_name == "sign_mismatch_drf_docs":
            response = {
                "scenario_id": 188,
                "scenario": "What are the documents required for sign mismatch in DRF",
                "path": "CBOS-2.0 > customer services > circulars & info",
                "type_of_process": "Process",
            }

        # Scenario 189
        elif api_name == "name_mismatch_drf_docs":
            response = {
                "scenario_id": 189,
                "scenario": "What are the documents required for name mismatch",
                "path": "CBOS-2.0 > customer services > circulars & info",
                "type_of_process": "Process",
            }

        # Scenario 190
        elif api_name == "drf_equity_vs_mf":
            response = {
                "scenario_id": 190,
                "scenario": "Is DRF for Equity and Mutual Fund different?",
                "path": "CBOS-2.0 >>DP >>download form",
                "type_of_process": "Process",
            }

        # Scenario 192
        elif api_name == "rrf_process":
            response = {
                "scenario_id": 192,
                "scenario": "RRF process",
                "path": "CBOS-2.0 >> Customer service >> Circular and info >> Downloads",
                "type_of_process": "Process",
            }

        # Scenario 195
        elif api_name == "rrf_checklist":
            response = {
                "scenario_id": 195,
                "scenario": "Checklist / Documents required for RRF",
                "path": "CBOS-2.0 >>dp >>download form",
                "type_of_process": "Process",
            }

        # Scenario 197
        elif api_name == "check_bsda_status":
            response = {
                "scenario_id": 197,
                "scenario": "Where can I check my BSDA status?",
                "path": "Rise App>>Profile>>Help & Support>>Chat With Us>>Digi CMR Report",
                "type_of_process": "Process",
            }

        # Scenario 202
        elif api_name == "how_to_know_bsda_flag":
            response = {
                "scenario_id": 202,
                "scenario": "How to know if an account is mapped under BSDA flag",
                "path": "CBOS-2.0 > Client view > BSDA flag",
                "type_of_process": "Process",
            }

        # Scenario 210
        elif api_name == "ledger_debit_after_funds_transfer":
            response = {
                "scenario_id": 210,
                "scenario": "Why is there a debit entry after funds transfer?",
                "path": "N/A",
                "type_of_process": "Process",
            }

        # Scenario 211
        elif api_name == "how_to_change_dp_scheme":
            response = {
                "scenario_id": 211,
                "scenario": "How to change scheme",
                "path": "CBOS-2.0 >>Depository>>Request>>DP scheme modification",
                "type_of_process": "Process",
            }

        # Scenario 221
        elif api_name == "check_pledge_status":
            response = {
                "scenario_id": 221,
                "scenario": "How we can check the pledge status?",
                "path": "CBOS-2.0 > Depository > Reports > Holding cum transaction",
                "type_of_process": "Process",
            }

        # Scenario 223
        elif api_name == "ba_deposit_for_nsdl_dp":
            response = {
                "scenario_id": 223,
                "scenario": "Can BA deposit be accepted for NSDL DP?",
                "path": (
                    "CBOS-2.0 >> Depository >> Request >> Pledge request >> "
                    "PLEDGOR DP (BA DP) >> Pledgee DP (MOFSL:1201090011337371) >> Agreement no >> "
                    "Tick BA deposit checkbox >> mention pledge value"
                ),
                "type_of_process": "Process",
            }

        # Scenario 225
        elif api_name == "ba_check_pledge_request_status":
            response = {
                "scenario_id": 225,
                "scenario": "How BA can check the status of Pledge request punched in CBOS",
                "path": "CBOS-2.0 >> Depository >> REPORTS >> Select date range",
                "type_of_process": "Process",
            }

        # Scenario 226
        elif api_name == "offline_pledge_request_rejected":
            response = {
                "scenario_id": 226,
                "scenario": "Offline Pledge request got rejected",
                "path": "CBOS-2.0 > Depository > reports > pledge/unpledged reports",
                "type_of_process": "Status",
            }

        # Scenario 227
        elif api_name == "check_ba_security_deposit":
            response = {
                "scenario_id": 227,
                "scenario": "How to check BA security deposit",
                "path": "CBOS-2.0 >> External Links >> Risk lab >> Reports >> Channel Risk",
                "type_of_process": "Process",
            }

        # Scenario 228
        elif api_name == "tat_for_ba_deposit_pledge":
            response = {
                "scenario_id": 228,
                "scenario": "TAT for BA deposit request for pledge",
                "path": "CBOS-2.0 >> Depository >> Reports >>Pledge/Unpledged report",
                "type_of_process": "Process",
            }

        # Scenario 233
        elif api_name == "loan_pledge_which_dp":
            response = {
                "scenario_id": 233,
                "scenario": "For loan pledge request in which DP client needs to activate",
                "path": "N/A",
                "type_of_process": "Process",
            }

        # Scenario 236
        elif api_name == "why_unpledged_rejected":
            response = {
                "scenario_id": 236,
                "scenario": "Why unpledged request got rejected",
                "path": "CBOS-2.0 >> DEPOSITORY >> REQUEST >> PLEDGE / UNPLEDGE >> REJECTED RECORDS",
                "type_of_process": "Process",
            }

        # Scenario 239
        elif api_name == "loan_pledge_request_rejected":
            response = {
                "scenario_id": 239,
                "scenario": "Loan Pledge request got rejected",
                "path": "CBOS-2.0 >> DEPOSITORY >> REQUEST >> PLEDGE / UNPLEDGE >> REJECTED RECORDS",
                "type_of_process": "Process",
            }

        # Scenario 868
        elif api_name == "drf_delete_request":
            response = {
                "scenario_id": 868,
                "scenario": "DRF Delete request",
                "path": "CBOS-2.0 >> Depository >> Request >> DRF RRF request >> Rejected records",
                "type_of_process": "Process",
            }

        # Scenario 869
        elif api_name == "charges_for_scheme_off_market":
            response = {
                "scenario_id": 869,
                "scenario": "What will be the charges for the scheme // off market transaction charges",
                "path": "CBOS-2.0 >> Dashboard >> Client Profile >> DP details",
                "type_of_process": "Process",
            }

        # Scenario 870
        elif api_name == "provide_pledge_form":
            response = {
                "scenario_id": 870,
                "scenario": "Provide pledge form",
                "path": "CBOS-2.0 >> depository >> Download forms",
                "type_of_process": "Process",
            }

        else:
            response = {"error": "Unknown api_name or no matching scenario."}

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response)

        return response

class Dp_api_callerTool(BaseTool):
    name: str = "dp_api_caller"
    description: str = """Description:
    The api_caller function is designed to handle and return data for various
    operational or support-related scenarios that require an API. The function
    takes in:

    1) api_name (str): A string specifying which scenario or operation to perform.
    2) api_args (dict): An optional dictionary of arguments that can be used
       for processing or filtering. Its usage may vary depending on the specific
       scenario.

    Return Value:
    A dictionary (JSON-like) containing:
      - scenario_id: Numeric identifier of the scenario.
      - scenario: A brief description of the situation or question.
      - path: The path or steps typically taken in a support tool (CBOS-2.0) or
        user portal to handle the request.
      - type_of_process: The type of the process (e.g., Status, Process, Technical).
      - additional fields or notes relevant to that scenario.

    Usage:
    This function centralizes all possible “api_required” scenarios so that
    a conversational or automation agent can retrieve the correct handling steps
    and references for each specific request. The structure may be expanded or
    replaced by real API integrations in the future."""
    args_schema: Type[BaseModel] = Dp_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return dp_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return dp_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

class Edp_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: dict = Field(default={}, description='Argument api_args')

def edp_api_caller(api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None) -> dict:
        """
        This function orchestrates calls to various CBOS-related endpoints. It accepts:

        1. api_name (str):
           Identifies the specific CBOS API/process to be executed.
           Supported values include:
             - "generate_gst_b2b_report"
             - "generate_ledger"
             - "fetch_contract_note_details"
             - "get_levies_and_charges_details"
             - "get_brokerage_details"
             - "generate_contract_note"
             - "generate_auction_bill"
             - "generate_physical_settlement_contract_note"
             - "generate_cash_bill"
             - "generate_fno_bill"
             - "generate_commodity_bill"
             - "generate_mf_bill"
             - "generate_slbm_bill"

        2. api_args (dict, optional):
           A dictionary containing any additional arguments required by the chosen API.
           Depending on the operation, this could include client IDs, date ranges,
           instrument types, or other relevant parameters.

        Returns:
           A dictionary containing the outcome of the requested operation, including
           status and pertinent data. The structure and fields of the dictionary
           will correspond to the specific API call.

        Usage Examples:
           1. api_caller("generate_ledger", {"client_id": "AB1234", "from_date": "2023-01-01", "to_date": "2023-02-01"})
           2. api_caller("generate_auction_bill", {"client_id": "CD5678", "bill_date": "2023-03-15"})
        """

        if api_name == "generate_gst_b2b_report":
            # Scenario 745: Generating or retrieving GST B2B invoices.
            # api_args may include date range, client info, etc.
            response = {
                "status": "success",
                "message": "GST B2B report generated successfully.",
                "report_available_date": "10th of the following month",
                "invoices": [
                    {
                        "invoice_id": "INV001",
                        "invoice_date": "2023-08-11",
                        "amount": 10000,
                        "gst_details": "GST details here",
                    }
                ],
            }

        elif api_name == "generate_ledger":
            # Scenario 751: Clarification of ledger debit.
            # api_args might include client_id, date range, ledger type, etc.
            response = {
                "status": "success",
                "message": "Ledger generated successfully.",
                "ledger_details": {
                    "client_id": api_args.get("client_id", "UNKNOWN"),
                    "transactions": [
                        {
                            "date": "2023-07-10",
                            "description": "Debit transaction",
                            "amount": 5000,
                        },
                        {
                            "date": "2023-07-12",
                            "description": "Credit transaction",
                            "amount": 2000,
                        },
                    ],
                },
            }

        elif api_name == "fetch_contract_note_details":
            # Scenario 756: Clarification of Contract Note
            # api_args might include contract_note_id, client_id, etc.
            response = {
                "status": "success",
                "message": "Contract note details fetched successfully.",
                "contract_note": {
                    "contract_note_id": "CN12345",
                    "trades": [
                        {"symbol": "ABC", "quantity": 100, "price": 250},
                        {"symbol": "XYZ", "quantity": 50, "price": 120},
                    ],
                },
            }

        elif api_name == "get_levies_and_charges_details":
            # Scenario 757: Calculation of other charges in contract note
            # api_args may include trade_date, segment, or client_id.
            response = {
                "status": "success",
                "message": "Levies and charges details retrieved.",
                "levies_info": [
                    {"charge_type": "Transaction Fee", "amount": 20},
                    {"charge_type": "Stamp Duty", "amount": 5},
                ],
                "brokerage_info": {"rate": 0.02, "min_brokerage": 30},
            }

        elif api_name == "get_brokerage_details":
            # Scenario 758: Brokerage charge applicable to the client
            # api_args might include client_id or segment to get the correct slab.
            response = {
                "status": "success",
                "message": "Brokerage details fetched.",
                "brokerage_slabs": {
                    "equity": "0.50% or min ₹30",
                    "derivatives": "₹20 per order",
                    "currency": "₹10 per order",
                },
            }

        elif api_name == "generate_contract_note":
            # Scenario 759: How to generate contract note
            response = {
                "status": "success",
                "message": "Contract note generated successfully.",
                "contract_note_link": "https://cbos.motilaloswal.com/contractnote/12345",
            }

        elif api_name == "generate_auction_bill":
            # Scenario 760: How to generate auction bill
            response = {
                "status": "success",
                "message": "Auction bill generated successfully.",
                "auction_bill_link": "https://cbos.motilaloswal.com/auctionbill/7890",
            }

        elif api_name == "generate_physical_settlement_contract_note":
            # Scenario 761: How to generate physical settlement contract note
            response = {
                "status": "success",
                "message": "Physical settlement contract note generated successfully.",
                "physical_bill_link": "https://cbos.motilaloswal.com/physicalsettlement/4567",
            }

        elif api_name == "generate_cash_bill":
            # Scenario 762: How to generate cash bill
            response = {
                "status": "success",
                "message": "Cash bill generated successfully.",
                "cash_bill_link": "https://cbos.motilaloswal.com/cashbill/2345",
            }

        elif api_name == "generate_fno_bill":
            # Scenario 763: How to generate FNO Bill
            response = {
                "status": "success",
                "message": "FNO bill generated successfully.",
                "fno_bill_link": "https://cbos.motilaloswal.com/fnobill/5678",
            }

        elif api_name == "generate_commodity_bill":
            # Scenario 764: How to generate Commodity Bill
            response = {
                "status": "success",
                "message": "Commodity bill generated successfully.",
                "commodity_bill_link": "https://cbos.motilaloswal.com/commoditybill/9876",
            }

        elif api_name == "generate_mf_bill":
            # Scenario 765: How to generate MF Bill
            response = {
                "status": "success",
                "message": "Mutual Fund bill generated successfully.",
                "mf_bill_link": "https://cbos.motilaloswal.com/mfbill/5432",
            }

        elif api_name == "generate_slbm_bill":
            # Scenario 766: How to generate SLBM Bill
            response = {
                "status": "success",
                "message": "SLBM bill generated successfully.",
                "slbm_bill_link": "https://cbos.motilaloswal.com/slbmbill/1122",
            }

        else:
            response = {
                "status": "failed",
                "message": f"Invalid api_name provided: {api_name}",
            }

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response)

        return response

class Edp_api_callerTool(BaseTool):
    name: str = "edp_api_caller"
    description: str = """This function orchestrates calls to various CBOS-related endpoints. It accepts:

1. api_name (str):
   Identifies the specific CBOS API/process to be executed.
   Supported values include:
     - "generate_gst_b2b_report"
     - "generate_ledger"
     - "fetch_contract_note_details"
     - "get_levies_and_charges_details"
     - "get_brokerage_details"
     - "generate_contract_note"
     - "generate_auction_bill"
     - "generate_physical_settlement_contract_note"
     - "generate_cash_bill"
     - "generate_fno_bill"
     - "generate_commodity_bill"
     - "generate_mf_bill"
     - "generate_slbm_bill"

2. api_args (dict, optional):
   A dictionary containing any additional arguments required by the chosen API.
   Depending on the operation, this could include client IDs, date ranges,
   instrument types, or other relevant parameters.

Returns:
   A dictionary containing the outcome of the requested operation, including
   status and pertinent data. The structure and fields of the dictionary
   will correspond to the specific API call.

Usage Examples:
   1. api_caller("generate_ledger", {"client_id": "AB1234", "from_date": "2023-01-01", "to_date": "2023-02-01"})
   2. api_caller("generate_auction_bill", {"client_id": "CD5678", "bill_date": "2023-03-15"})"""
    args_schema: Type[BaseModel] = Edp_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return edp_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return edp_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

class Front_office_sales_query_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: dict = Field(default={}, description='Argument api_args')

def front_office_sales_query_api_caller(
        api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None
    ) -> dict:
        """
        This function serves as a unified entry point for calling various internal services
        that cover branding and marketing material needs. It supports multiple operations,
        each distinguishable by the 'api_name' parameter.

        Parameters
        ----------
        api_name : str
            The specific API endpoint name to invoke. Supported values include:

            1. "request_branding_material"
               - Places a new order for any marketing or branding materials
                 (e.g., logo, visiting cards, flex boards, banners, standee, canopy, etc.)
               - Arguments (pass within api_args):
                   - material_type (str): Type of material, e.g. "Flex board", "Visiting card", etc.
                   - branch_code (str, optional): Code or identifier of the requesting branch/franchise.
                   - quantity (int, optional): Number of items requested.
                   - dimensions (str, optional): Required dimensions (e.g., "6x3" for a banner).
                   - priority (str, optional): Indicate if the request is "normal" or "urgent".
                   - any other relevant information necessary for ordering.

            2. "check_branding_order_status"
               - Fetches the status of an existing branding or marketing-material order.
               - Arguments (pass within api_args):
                   - order_id (str): A unique identifier for the placed order.
                   - branch_code (str, optional): Code or identifier of the requesting branch/franchise (if needed).

            3. "initiate_branding_approval"
               - Initiates or checks approvals needed for branding creatives or advertisements.
               - Arguments (pass within api_args):
                   - creative_details (str): Detailed description of the creative or advertisement content.
                   - branch_code (str, optional): Code or identifier of the requesting branch.
                   - additional_notes (str, optional): Additional remarks or clarifications required for approval.

        api_args : dict, optional
            A dictionary of arguments relevant to the chosen API operation.

        Returns
        -------
        dict
            A JSON-like dictionary containing the response for the invoked API. In real usage,
            this would be replaced by the actual external or internal service response.
            Typical fields might include:
                 - status_code (int)
                 - message (str)
                 - order_id, approval_id, or any other data point if applicable.

        Notes
        -----
        - The scenarios identified (603 to 616) all require some interaction that can be handled
          by one of the above three API calls.
        - Adjust or extend the APIs as needed to fully accommodate any particular scenario.
        """

        if api_name == "request_branding_material":
            # This branch handles placing a new branding/material order
            response = {
                "status_code": 200,
                "message": "Branding material request placed successfully.",
                "requested_item": api_args.get("material_type", "unspecified"),
                "order_id": "ORDER-12345",  # Sample placeholder
            }

        elif api_name == "check_branding_order_status":
            # This branch checks for the status of an existing order
            order_id = api_args.get("order_id", "N/A")
            response = {
                "status_code": 200,
                "order_id": order_id,
                "current_status": "In Process",  # Could be Shipped, Delivered, etc.
                "estimated_completion": "T+15 working days",
                "message": "Order status retrieved.",
            }

        elif api_name == "initiate_branding_approval":
            # This branch handles submission or query of branding approvals
            creative_details = api_args.get("creative_details", "N/A")
            response = {
                "status_code": 200,
                "approval_id": "APPROVAL-67890",  # Sample placeholder
                "creative_details_received": creative_details,
                "message": "Branding approval process initiated.",
            }

        else:
            # Handles any unrecognized API name
            response = {
                "status_code": 404,
                "message": "The specified API endpoint was not found.",
            }

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response)

        return response

class Front_office_sales_query_api_callerTool(BaseTool):
    name: str = "front_office_sales_query_api_caller"
    description: str = """This function serves as a unified entry point for calling various internal services
that cover branding and marketing material needs. It supports multiple operations,
each distinguishable by the 'api_name' parameter.

Parameters
----------
api_name : str
    The specific API endpoint name to invoke. Supported values include:

    1. "request_branding_material"
       - Places a new order for any marketing or branding materials
         (e.g., logo, visiting cards, flex boards, banners, standee, canopy, etc.)
       - Arguments (pass within api_args):
           - material_type (str): Type of material, e.g. "Flex board", "Visiting card", etc.
           - branch_code (str, optional): Code or identifier of the requesting branch/franchise.
           - quantity (int, optional): Number of items requested.
           - dimensions (str, optional): Required dimensions (e.g., "6x3" for a banner).
           - priority (str, optional): Indicate if the request is "normal" or "urgent".
           - any other relevant information necessary for ordering.

    2. "check_branding_order_status"
       - Fetches the status of an existing branding or marketing-material order.
       - Arguments (pass within api_args):
           - order_id (str): A unique identifier for the placed order.
           - branch_code (str, optional): Code or identifier of the requesting branch/franchise (if needed).

    3. "initiate_branding_approval"
       - Initiates or checks approvals needed for branding creatives or advertisements.
       - Arguments (pass within api_args):
           - creative_details (str): Detailed description of the creative or advertisement content.
           - branch_code (str, optional): Code or identifier of the requesting branch.
           - additional_notes (str, optional): Additional remarks or clarifications required for approval.

api_args : dict, optional
    A dictionary of arguments relevant to the chosen API operation.

Returns
-------
dict
    A JSON-like dictionary containing the response for the invoked API. In real usage,
    this would be replaced by the actual external or internal service response.
    Typical fields might include:
         - status_code (int)
         - message (str)
         - order_id, approval_id, or any other data point if applicable.

Notes
-----
- The scenarios identified (603 to 616) all require some interaction that can be handled
  by one of the above three API calls.
- Adjust or extend the APIs as needed to fully accommodate any particular scenario."""
    args_schema: Type[BaseModel] = Front_office_sales_query_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return front_office_sales_query_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return front_office_sales_query_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

class Mo_genie_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: dict = Field(default={}, description='Argument api_args')

def mo_genie_api_caller(api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None) -> dict:
        """
        Function Name
        -------------
        api_caller

        Description
        -----------
        This function is intended to handle calls for scenarios where an API is required
        (e.g., placing marketing/branding material requests, checking order status,
        requesting branding approvals, etc.). The arguments and return structures vary
        depending on the api_name parameter.

        Parameters
        ----------
        api_name : str
            Specifies which API route or action to perform. It can be one of:
              1. 'requestBrandingMaterial'
                  - Used for placing or updating a request for branding/marketing material
                    (e.g., logo, flex board, banner, etc.).
                  - Expected api_args might include:
                      material_type  : str  (e.g., 'logo', 'banner', 'visiting_card_format')
                      quantity       : int  (optional, number of items)
                      branch_id      : str  (optional, branch or user identifier)
                      notes          : str  (optional, additional instructions)
                  - Returns a dict with details about the submitted request.

              2. 'checkBrandingMaterialOrderStatus'
                  - Used to check the status of an already placed branding/marketing material order.
                  - Expected api_args might include:
                      request_id     : str  (the ID for tracking the order)
                  - Returns current status, expected delivery date, etc.

              3. 'requestBrandingApproval'
                  - Used for obtaining branding design or text approvals from the relevant team.
                  - Expected api_args might include:
                      branding_text     : str   (the material or text to approve)
                      disclaimer        : str   (any required disclaimers or warnings)
                      license_details   : str   (licensing or registration details)
                  - Returns the approval status, remarks, or any required corrections.

        Returns
        -------
        dict
            A dictionary representing the response from the chosen API route. Contains
            status information, request identifiers, remarks, or other relevant data.
        """

        response = {}

        if api_name == "requestBrandingMaterial":
            # For placing or updating a branding/marketing material request
            response = {
                "status": "success",
                "request_id": "BR-202310100001",
                "estimated_tat_days": 15,
                "message": "Branding material request has been placed successfully.",
            }

        elif api_name == "checkBrandingMaterialOrderStatus":
            # For checking the current status of an existing branding/material order
            response = {
                "status": "in_process",
                "request_id": api_args.get("request_id", "Not Provided"),
                "current_stage": "Printing",
                "expected_delivery_date": "2023-12-01",
                "comments": "Your order is currently in process. We will notify you once shipped.",
            }

        elif api_name == "requestBrandingApproval":
            # For requesting approvals related to branding text, creative, or design
            response = {
                "status": "received",
                "approval_status": "pending",
                "remarks": "Please ensure all official disclaimers are added.",
                "expected_approval_date": "2023-10-20",
            }

        else:
            response = {"error": "Invalid API name specified."}

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response)

        return response

class Mo_genie_api_callerTool(BaseTool):
    name: str = "mo_genie_api_caller"
    description: str = """Function Name
-------------
api_caller

Description
-----------
This function is intended to handle calls for scenarios where an API is required
(e.g., placing marketing/branding material requests, checking order status,
requesting branding approvals, etc.). The arguments and return structures vary
depending on the api_name parameter.

Parameters
----------
api_name : str
    Specifies which API route or action to perform. It can be one of:
      1. 'requestBrandingMaterial'
          - Used for placing or updating a request for branding/marketing material
            (e.g., logo, flex board, banner, etc.).
          - Expected api_args might include:
              material_type  : str  (e.g., 'logo', 'banner', 'visiting_card_format')
              quantity       : int  (optional, number of items)
              branch_id      : str  (optional, branch or user identifier)
              notes          : str  (optional, additional instructions)
          - Returns a dict with details about the submitted request.

      2. 'checkBrandingMaterialOrderStatus'
          - Used to check the status of an already placed branding/marketing material order.
          - Expected api_args might include:
              request_id     : str  (the ID for tracking the order)
          - Returns current status, expected delivery date, etc.

      3. 'requestBrandingApproval'
          - Used for obtaining branding design or text approvals from the relevant team.
          - Expected api_args might include:
              branding_text     : str   (the material or text to approve)
              disclaimer        : str   (any required disclaimers or warnings)
              license_details   : str   (licensing or registration details)
          - Returns the approval status, remarks, or any required corrections.

Returns
-------
dict
    A dictionary representing the response from the chosen API route. Contains
    status information, request identifiers, remarks, or other relevant data."""
    args_schema: Type[BaseModel] = Mo_genie_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return mo_genie_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return mo_genie_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

class Modification_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: dict = Field(default={}, description='Argument api_args')

def modification_api_caller(api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None) -> dict:
        """
        The 'api_caller' function acts as a unified interface to call various APIs
        related to branding and marketing material handling. It covers:

        1) Creating new marketing collateral orders.
        2) Checking the status of existing collateral orders.
        3) Retrieving branding approval details.

        Parameters:
        -----------
        api_name : str
            The identifier of the API being called. Supported values are:
              - "create_marketing_collateral_order"
              - "check_marketing_collateral_status"
              - "fetch_branding_approval_details"

        api_args : dict (optional)
            A dictionary containing the arguments relevant to the specific API call.
            Examples for each:

            A) For "create_marketing_collateral_order":
               {
                 "partner_id": "string",
                 "materials_requested": ["Flex Board", "Visiting Card Format", "Umbrella"],
                 "quantity_info": {"Flex Board": 2, "Visiting Card Format": 100, "Umbrella": 1},
                 "remarks": "Remarks or special instructions"
               }

            B) For "check_marketing_collateral_status":
               {
                 "order_id": "string"
               }

            C) For "fetch_branding_approval_details":
               {
                 "approval_reference": "AYAC1200"
               }

        Returns:
        --------
        dict
            A JSON-compatible dictionary representing the result of the API call.
            The structure of the response will differ depending on the method invoked.
            Typical examples:

            A) If api_name is "create_marketing_collateral_order":
               {
                 "status": "order_created",
                 "order_id": "ABC12345",
                 "estimated_time_of_arrival": "T+15 working days"
               }

            B) If api_name is "check_marketing_collateral_status":
               {
                 "order_id": "ABC12345",
                 "status": "in_process",
                 "date_of_request": "2023-09-20",
                 "expected_completion": "2023-10-05",
                 "reason_for_delay": ""
               }

            C) If api_name is "fetch_branding_approval_details":
               {
                 "approval_reference": "AYAC1200",
                 "observations": [
                     "Please add complete disclaimer",
                     "Recheck the framing of promotional text"
                 ],
                 "current_status": "Pending",
                 "comments": "Kindly submit revised copy for further review"
               }

        Usage:
        ------
        Call this function with the appropriate 'api_name' and 'api_args' depending
        on the scenario you need to handle.
        """

        if api_name == "create_marketing_collateral_order":
            response = {
                "status": "order_created",
                "order_id": "ABC12345",
                "estimated_time_of_arrival": "T+15 working days",
            }

        elif api_name == "check_marketing_collateral_status":
            response = {
                "order_id": api_args.get("order_id", ""),
                "status": "in_process",
                "date_of_request": "2023-09-25",
                "expected_completion": "2023-10-10",
                "reason_for_delay": "",
            }

        elif api_name == "fetch_branding_approval_details":
            response = {
                "approval_reference": api_args.get("approval_reference", ""),
                "observations": [
                    "Please add complete disclaimer",
                    "Recheck the framing of promotional text",
                ],
                "current_status": "Pending",
                "comments": "Kindly submit revised copy for further review",
            }

        else:
            response = {"error": "Invalid api_name provided."}

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response)

        return response

class Modification_api_callerTool(BaseTool):
    name: str = "modification_api_caller"
    description: str = """The 'api_caller' function acts as a unified interface to call various APIs
related to branding and marketing material handling. It covers:

1) Creating new marketing collateral orders.
2) Checking the status of existing collateral orders.
3) Retrieving branding approval details.

Parameters:
-----------
api_name : str
    The identifier of the API being called. Supported values are:
      - "create_marketing_collateral_order"
      - "check_marketing_collateral_status"
      - "fetch_branding_approval_details"

api_args : dict (optional)
    A dictionary containing the arguments relevant to the specific API call.
    Examples for each:

    A) For "create_marketing_collateral_order":
       {
         "partner_id": "string",
         "materials_requested": ["Flex Board", "Visiting Card Format", "Umbrella"],
         "quantity_info": {"Flex Board": 2, "Visiting Card Format": 100, "Umbrella": 1},
         "remarks": "Remarks or special instructions"
       }

    B) For "check_marketing_collateral_status":
       {
         "order_id": "string"
       }

    C) For "fetch_branding_approval_details":
       {
         "approval_reference": "AYAC1200"
       }

Returns:
--------
dict
    A JSON-compatible dictionary representing the result of the API call.
    The structure of the response will differ depending on the method invoked.
    Typical examples:

    A) If api_name is "create_marketing_collateral_order":
       {
         "status": "order_created",
         "order_id": "ABC12345",
         "estimated_time_of_arrival": "T+15 working days"
       }

    B) If api_name is "check_marketing_collateral_status":
       {
         "order_id": "ABC12345",
         "status": "in_process",
         "date_of_request": "2023-09-20",
         "expected_completion": "2023-10-05",
         "reason_for_delay": ""
       }

    C) If api_name is "fetch_branding_approval_details":
       {
         "approval_reference": "AYAC1200",
         "observations": [
             "Please add complete disclaimer",
             "Recheck the framing of promotional text"
         ],
         "current_status": "Pending",
         "comments": "Kindly submit revised copy for further review"
       }

Usage:
------
Call this function with the appropriate 'api_name' and 'api_args' depending
on the scenario you need to handle."""
    args_schema: Type[BaseModel] = Modification_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return modification_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return modification_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

class Mtf_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: dict = Field(default={}, description='Argument api_args')

def mtf_api_caller(api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None) -> dict:
        """
        Description:
            This function provides a unified interface to call various APIs required
            for handling branding-related requests. It covers:
              - Requesting new branding material (logos, flex boards, standees, etc.)
              - Checking the status of an existing branding-material order
              - Requesting branding approval for specific creatives

        Parameters:
        -----------
        api_name : str
            Name of the API to be called. Possible values:
                1) "requestBrandingMaterial"
                2) "checkBrandingMaterialStatus"
                3) "requestBrandingApproval"

        api_args : dict, optional
            A dictionary of arguments required for the chosen API.
            Fields vary based on the api_name:

            When api_name = "requestBrandingMaterial":
                - "branch_id" (str): Unique identifier of the branch/franchise
                - "material_type" (str): Type of material needed (e.g., "Logo",
                                         "Flex Board", "Visiting Card", "Umbrella", "Standee", etc.)
                - "quantity" (int, optional): Quantity required
                - "additional_notes" (str, optional): Any extra details

            When api_name = "checkBrandingMaterialStatus":
                - "order_id" (str): The order ID for which status is being queried

            When api_name = "requestBrandingApproval":
                - "creative_id" (str): A reference to the specific creative or advertisement
                - "license_details" (str, optional): PMS, IAP, Insurance License used
                - "disclaimer_included" (bool, optional): Whether disclaimers have been added
                - "revisions" (list, optional): List of changes or feedback points incorporated

        Returns:
        --------
        dict
            A JSON-like dictionary containing the response from the called API.
            The structure of the returned dictionary depends on the api_name:

            For "requestBrandingMaterial":
                {
                  "order_id": str,
                  "status": str,
                  "message": str,
                  "estimated_delivery": str
                }

            For "checkBrandingMaterialStatus":
                {
                  "order_id": str,
                  "current_status": str,
                  "date_of_request": str,
                  "expected_completion": str,
                  "remarks": str
                }

            For "requestBrandingApproval":
                {
                  "approval_id": str,
                  "status": str,
                  "feedback": str,
                  "additional_requirements": str
                }

        Notes:
        ------
        • The function covers all scenarios where an API call is required (from scenario_id 603 to 616).
        • Each 'api_name' branch simulates the process of sending and receiving data
          related to branding material or approval requests.
        • Actual implementation (integrating with live systems) will replace
          these response structures externally.
        """

        response = {}

        if api_name == "requestBrandingMaterial":
            # Example response structure after "requesting" branding material
            response = {
                "order_id": "BRD-20231011-XYZ",
                "status": "Order Placed",
                "message": "Your request for branding material has been received.",
                "estimated_delivery": "T+15 working days",
            }

        elif api_name == "checkBrandingMaterialStatus":
            # Example response structure for checking an existing order's status
            response = {
                "order_id": api_args.get("order_id", "Unknown"),
                "current_status": "In Process",
                "date_of_request": "2023-10-01",
                "expected_completion": "2023-10-16",
                "remarks": "Order is being processed by the branding team.",
            }

        elif api_name == "requestBrandingApproval":
            # Example response structure for requesting branding approval
            response = {
                "approval_id": "APPR-AYAC1200",
                "status": "Pending Review",
                "feedback": "Requires standard warning and disclaimers",
                "additional_requirements": "For any modifications, email nishchaya.sadhwani or ruchi.varma",
            }

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response)

        return response

class Mtf_api_callerTool(BaseTool):
    name: str = "mtf_api_caller"
    description: str = """Description:
    This function provides a unified interface to call various APIs required
    for handling branding-related requests. It covers:
      - Requesting new branding material (logos, flex boards, standees, etc.)
      - Checking the status of an existing branding-material order
      - Requesting branding approval for specific creatives

Parameters:
-----------
api_name : str
    Name of the API to be called. Possible values:
        1) "requestBrandingMaterial"
        2) "checkBrandingMaterialStatus"
        3) "requestBrandingApproval"

api_args : dict, optional
    A dictionary of arguments required for the chosen API.
    Fields vary based on the api_name:

    When api_name = "requestBrandingMaterial":
        - "branch_id" (str): Unique identifier of the branch/franchise
        - "material_type" (str): Type of material needed (e.g., "Logo",
                                 "Flex Board", "Visiting Card", "Umbrella", "Standee", etc.)
        - "quantity" (int, optional): Quantity required
        - "additional_notes" (str, optional): Any extra details

    When api_name = "checkBrandingMaterialStatus":
        - "order_id" (str): The order ID for which status is being queried

    When api_name = "requestBrandingApproval":
        - "creative_id" (str): A reference to the specific creative or advertisement
        - "license_details" (str, optional): PMS, IAP, Insurance License used
        - "disclaimer_included" (bool, optional): Whether disclaimers have been added
        - "revisions" (list, optional): List of changes or feedback points incorporated

Returns:
--------
dict
    A JSON-like dictionary containing the response from the called API.
    The structure of the returned dictionary depends on the api_name:

    For "requestBrandingMaterial":
        {
          "order_id": str,
          "status": str,
          "message": str,
          "estimated_delivery": str
        }

    For "checkBrandingMaterialStatus":
        {
          "order_id": str,
          "current_status": str,
          "date_of_request": str,
          "expected_completion": str,
          "remarks": str
        }

    For "requestBrandingApproval":
        {
          "approval_id": str,
          "status": str,
          "feedback": str,
          "additional_requirements": str
        }

Notes:
------
• The function covers all scenarios where an API call is required (from scenario_id 603 to 616).
• Each 'api_name' branch simulates the process of sending and receiving data
  related to branding material or approval requests.
• Actual implementation (integrating with live systems) will replace
  these response structures externally."""
    args_schema: Type[BaseModel] = Mtf_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return mtf_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return mtf_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

class Operations_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: dict = Field(default={}, description='Argument api_args')

def operations_api_caller(api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None) -> dict:
        """
        The 'api_caller' function is designed to interact with various internal
        Branding and Marketing APIs. It uses the 'api_name' to determine which
        operation should be performed and processes the 'api_args' accordingly.

        Supported API endpoints:

        1. place_marketing_collateral_order
           Description:
             - Creates a new marketing collateral order (e.g., logo, banner, visiting cards, boards).
           Expected api_args:
             - branch_id (str): The identifying code for the branch or franchise requesting the materials.
             - material_type (str): The type of marketing material being ordered (e.g., Banner, Flex board).
             - quantity (int): Number of units requested.
             - needed_by (str): The required date or any indication of urgency.
           Return Value (dict):
             - order_id (str): A unique identifier for the newly created order.
             - order_status (str): The current processing status (e.g. 'In Process').

        2. check_marketing_order_status
           Description:
             - Retrieves the current status of an existing marketing collateral order.
           Expected api_args:
             - order_id (str): The unique identifier of the order to be tracked.
           Return Value (dict):
             - order_id (str): Echoes back the requested order ID.
             - order_status (str): The current status of the order (e.g. 'In Process', 'Dispatched').
             - expected_delivery_date (str): Estimated completion or delivery date.
             - remarks (str): Additional details or explanations regarding the order (e.g. reason for delay).

        3. branding_approval
           Description:
             - Processes or retrieves the approval status for specific branding or marketing items.
           Expected api_args:
             - approval_id (str): A reference identifier for the branding approval request.
             - creative_details (dict, optional): Information about the creative material to be approved.
           Return Value (dict):
             - approval_status (str): The current approval state (e.g. 'Approved', 'Pending Review').
             - remarks (str): Additional notes or feedback about the approval process.

        Usage Example:
        response = api_caller(
            api_name="place_marketing_collateral_order",
            api_args={
                "branch_id": "BRANCH123",
                "material_type": "Flex Board",
                "quantity": 1,
                "needed_by": "2023-12-01"
            }
        )

        The function returns a dictionary containing the relevant response
        for the chosen API endpoint.
        """

        if api_name == "place_marketing_collateral_order":
            response = {"order_id": "ORD123456", "order_status": "In Process"}

        elif api_name == "check_marketing_order_status":
            response = {
                "order_id": api_args.get("order_id", "N/A"),
                "order_status": "Dispatched",
                "expected_delivery_date": "2023-11-15",
                "remarks": "Your requested items are on their way.",
            }

        elif api_name == "branding_approval":
            response = {
                "approval_status": "Pending Review",
                "remarks": "Under compliance check.",
            }

        else:
            response = {"error": "Unsupported API request."}

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response)

        return response

class Operations_api_callerTool(BaseTool):
    name: str = "operations_api_caller"
    description: str = """The 'api_caller' function is designed to interact with various internal
Branding and Marketing APIs. It uses the 'api_name' to determine which
operation should be performed and processes the 'api_args' accordingly.

Supported API endpoints:

1. place_marketing_collateral_order
   Description:
     - Creates a new marketing collateral order (e.g., logo, banner, visiting cards, boards).
   Expected api_args:
     - branch_id (str): The identifying code for the branch or franchise requesting the materials.
     - material_type (str): The type of marketing material being ordered (e.g., Banner, Flex board).
     - quantity (int): Number of units requested.
     - needed_by (str): The required date or any indication of urgency.
   Return Value (dict):
     - order_id (str): A unique identifier for the newly created order.
     - order_status (str): The current processing status (e.g. 'In Process').

2. check_marketing_order_status
   Description:
     - Retrieves the current status of an existing marketing collateral order.
   Expected api_args:
     - order_id (str): The unique identifier of the order to be tracked.
   Return Value (dict):
     - order_id (str): Echoes back the requested order ID.
     - order_status (str): The current status of the order (e.g. 'In Process', 'Dispatched').
     - expected_delivery_date (str): Estimated completion or delivery date.
     - remarks (str): Additional details or explanations regarding the order (e.g. reason for delay).

3. branding_approval
   Description:
     - Processes or retrieves the approval status for specific branding or marketing items.
   Expected api_args:
     - approval_id (str): A reference identifier for the branding approval request.
     - creative_details (dict, optional): Information about the creative material to be approved.
   Return Value (dict):
     - approval_status (str): The current approval state (e.g. 'Approved', 'Pending Review').
     - remarks (str): Additional notes or feedback about the approval process.

Usage Example:
response = api_caller(
    api_name="place_marketing_collateral_order",
    api_args={
        "branch_id": "BRANCH123",
        "material_type": "Flex Board",
        "quantity": 1,
        "needed_by": "2023-12-01"
    }
)

The function returns a dictionary containing the relevant response
for the chosen API endpoint."""
    args_schema: Type[BaseModel] = Operations_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return operations_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return operations_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

class Processing_activities_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: dict = Field(default={}, description='Argument api_args')

def processing_activities_api_caller(
        api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None
    ) -> dict:
        """
        Description:
            The 'api_caller' function serves as a single entry point for calling various
            APIs required to handle branding queries for Motilal Oswal (MO). It takes
            two parameters:

            1) api_name (str): Identifies which specific API you wish to call.
               Possible values in this context could be:
                   - 'place_marketing_collateral_order'
                   - 'check_marketing_collateral_order_status'
                   - 'request_branding_approval'

            2) api_args (dict): A dictionary containing the arguments to be passed to
               the chosen API. The keys and values inside 'api_args' will depend on
               the specific data each API method needs (e.g., order_id, branch_id,
               items_requested, approval_request_id, etc.).

            The function returns a JSON-compatible dictionary that includes the
            relevant data or status information. This dictionary should reflect
            what the calling context (e.g., a Gen AI agent) needs to know or convey
            to end users.
        """

        if api_name == "place_marketing_collateral_order":
            # Use this to place orders for marketing materials (logo, flex board, standee, etc.).
            # api_args might contain items_requested, branch_id, request_date, etc.
            response = {
                "status": "success",
                "message": "Marketing collateral order has been placed successfully.",
                "estimated_delivery_date": "T+15 working days from date_of_order",
                "items_requested": api_args.get("items_requested", []),
                "branch_id": api_args.get("branch_id", None),
            }

        elif api_name == "check_marketing_collateral_order_status":
            # Use this to check the status of an existing order when TAT is within
            # or has exceeded the expected timeframe.
            # api_args might contain order_id, or any reference to track the order.
            response = {
                "order_id": api_args.get("order_id", None),
                "order_status": "In Progress",
                "expected_delivery_date": "Date as per TAT",
                "remarks": "Your order is currently under process.",
            }

        elif api_name == "request_branding_approval":
            # Use this to handle branding approval scenarios (e.g., AYAC1200 Branding Approval).
            # api_args might include approval_request_id, creative_details, disclaimers, etc.
            response = {
                "approval_request_id": api_args.get("approval_request_id", "N/A"),
                "approval_status": "In Review",
                "remarks": (
                    "Please add appropriate disclaimers and registration number. "
                    "Resubmit for final approval."
                ),
            }

        else:
            # This handles the case where the API name doesn't match any known operation
            response = {
                "status": "error",
                "message": f"API name '{api_name}' is not recognized.",
            }

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response)

        return response

class Processing_activities_api_callerTool(BaseTool):
    name: str = "processing_activities_api_caller"
    description: str = """Description:
    The 'api_caller' function serves as a single entry point for calling various
    APIs required to handle branding queries for Motilal Oswal (MO). It takes
    two parameters:

    1) api_name (str): Identifies which specific API you wish to call.
       Possible values in this context could be:
           - 'place_marketing_collateral_order'
           - 'check_marketing_collateral_order_status'
           - 'request_branding_approval'

    2) api_args (dict): A dictionary containing the arguments to be passed to
       the chosen API. The keys and values inside 'api_args' will depend on
       the specific data each API method needs (e.g., order_id, branch_id,
       items_requested, approval_request_id, etc.).

    The function returns a JSON-compatible dictionary that includes the
    relevant data or status information. This dictionary should reflect
    what the calling context (e.g., a Gen AI agent) needs to know or convey
    to end users."""
    args_schema: Type[BaseModel] = Processing_activities_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return processing_activities_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return processing_activities_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

class Rms_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: dict = Field(default={}, description='Argument api_args')

def rms_api_caller(api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None) -> dict:
        """
        The `api_caller` function provides access to different operations related to Branding Queries
        for Marketing Collaterals, mirroring what CBOS might offer. This is used to handle queries
        that require an internal system/API call.

        Parameters
        ----------
        api_name : str
            The name of the API operation to perform. Possible values include:
            - "order_branding_material": Submit a request for marketing or branding materials.
            - "check_branding_material_status": Retrieve the status of a previously placed order.
            - "branding_approval": Submit or check a request for branding approval.

        api_args : dict, optional
            A dictionary of arguments required for the specific API. For example:

            For "order_branding_material", possible keys could be:
              {
                  "material_type": "string",
                  "branch_id": "string",
                  "quantity": int
                  // additional relevant details
              }

            For "check_branding_material_status", possible keys could be:
              {
                  "order_id": "string"
              }

            For "branding_approval", possible keys could be:
              {
                  "approval_id": "string",
                  "creative_details": "string",
                  "disclaimers": "string",
                  "license_details": "string"
                  // additional relevant details
              }

        Returns
        -------
        dict
            A JSON-like response object with information relevant to the requested operation.
            The exact structure depends on the 'api_name' branch invoked. For instance:
              {
                  "status": "Order submitted successfully",
                  "order_id": "ORDER1234",
                  ...
              }
              or
              {
                  "order_status": "In process",
                  "expected_completion_date": "2023-10-31",
                  ...
              }
              or
              {
                  "approval_status": "Pending",
                  "observations": [...],
                  ...
              }

        Usage
        -----
          response = api_caller("order_branding_material", {"material_type": "Flex Board", "branch_id": "ABC123", "quantity": 2})
          print(response)
        """

        if api_name == "order_branding_material":
            # Handles requests to place an order for MOFSL marketing or branding materials
            response = {
                "status": "Order submitted successfully",
                "order_id": "ORDER1234",
                "estimated_delivery_days": 15,
                "message": "Your request for branding material has been recorded.",
                "requested_materials": api_args.get("material_type", "Not specified"),
            }

        elif api_name == "check_branding_material_status":
            # Handles checking the status of an existing order
            response = {
                "order_id": api_args.get("order_id", None),
                "order_status": "In process",
                "expected_completion_date": "2023-10-31",
                "message": "Your branding material request is still under the standard TAT.",
            }

        elif api_name == "branding_approval":
            # Handles branding or advertising approvals (e.g., AYAC1200 approvals)
            response = {
                "approval_id": api_args.get("approval_id", None),
                "approval_status": "Pending review",
                "observations": [
                    "Confirm PMS, IAP, and Insurance License details if applicable.",
                    "Include full disclaimers and standard warning text.",
                ],
                "message": "Please revise or confirm the provided creative details as requested.",
            }

        else:
            # Fallback for any unrecognized API name
            response = {
                "status": "Invalid operation",
                "message": "The api_name provided does not match any known operation.",
            }

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response)

        return response

class Rms_api_callerTool(BaseTool):
    name: str = "rms_api_caller"
    description: str = """The `api_caller` function provides access to different operations related to Branding Queries
for Marketing Collaterals, mirroring what CBOS might offer. This is used to handle queries
that require an internal system/API call.

Parameters
----------
api_name : str
    The name of the API operation to perform. Possible values include:
    - "order_branding_material": Submit a request for marketing or branding materials.
    - "check_branding_material_status": Retrieve the status of a previously placed order.
    - "branding_approval": Submit or check a request for branding approval.

api_args : dict, optional
    A dictionary of arguments required for the specific API. For example:

    For "order_branding_material", possible keys could be:
      {
          "material_type": "string",
          "branch_id": "string",
          "quantity": int
          // additional relevant details
      }

    For "check_branding_material_status", possible keys could be:
      {
          "order_id": "string"
      }

    For "branding_approval", possible keys could be:
      {
          "approval_id": "string",
          "creative_details": "string",
          "disclaimers": "string",
          "license_details": "string"
          // additional relevant details
      }

Returns
-------
dict
    A JSON-like response object with information relevant to the requested operation.
    The exact structure depends on the 'api_name' branch invoked. For instance:
      {
          "status": "Order submitted successfully",
          "order_id": "ORDER1234",
          ...
      }
      or
      {
          "order_status": "In process",
          "expected_completion_date": "2023-10-31",
          ...
      }
      or
      {
          "approval_status": "Pending",
          "observations": [...],
          ...
      }

Usage
-----
  response = api_caller("order_branding_material", {"material_type": "Flex Board", "branch_id": "ABC123", "quantity": 2})
  print(response)"""
    args_schema: Type[BaseModel] = Rms_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return rms_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return rms_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

class Settlement_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: dict = Field(default={}, description='Argument api_args')

def settlement_api_caller(api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None) -> dict:
        """
        This function routes calls to various internal services that replace CBOS operations.

        Parameters:
        -----------
        api_name : str
            Name of the API to be invoked. Possible values include:
              1. "order_marketing_material"
                 Used for placing or requesting marketing/branding collateral
                 (e.g., flex boards, banners, visiting cards).
              2. "check_marketing_material_status"
                 Used for inquiring about the status (within or beyond TAT) of any
                 previously placed marketing material order.
              3. "branding_approval"
                 Used for submitting or checking approvals regarding branding
                 changes, logo updates, or regulatory disclaimers.

        api_args : dict, optional
            Arguments relevant to the chosen API. For example:
              - "order_marketing_material" might expect:
                  {
                      "material_type": str,    # e.g., "flex", "banner", "visiting_card"
                      "quantity": int,        # e.g., 10
                      "branch_code": str,     # e.g., "RPRITIJAIN"
                      "additional_notes": str # e.g., "Need updated logo version"
                  }
              - "check_marketing_material_status" might expect:
                  {
                      "order_id": str         # e.g., "MAT12345"
                  }
              - "branding_approval" might expect:
                  {
                      "request_id": str,      # e.g., "AYAC1200"
                      "creative_details": str # e.g., "Updated disclaimers, warnings"
                  }

        Returns:
        --------
        dict
            A JSON-like response object with the outcome of the requested operation.
            The actual keys depend on the nature of the called API. Typical fields
            might include:
              - "status": Indicates success/failure or current processing state.
              - "message": Brief explanation or additional context.
              - Any other relevant information such as "order_id", "expected_delivery",
                "comments", or "last_updated".

        Scenarios Covered (api_required = "Yes"):
        -----------------------------------------
        - Requesting new marketing material (scenario_ids: 603, 604, 605, 606, 607, 609,
          612, 613, 614, 615)
          => api_name = "order_marketing_material"
        - Checking marketing material order status (scenario_ids: 608, 611, 616, etc.)
          => api_name = "check_marketing_material_status"
        - Branding approval request (scenario_id: 610)
          => api_name = "branding_approval"
        """
        response = {}

        if api_name == "order_marketing_material":
            # Logic for placing or requesting marketing materials.
            response = {
                "status": "success",
                "message": "Marketing material request placed successfully.",
                "order_id": "MAT000123",
                "estimated_delivery": "2023-10-15",
            }

        elif api_name == "check_marketing_material_status":
            # Logic for retrieving status of a previously placed marketing material order.
            # Typically requires an "order_id" in api_args.
            order_id = api_args.get("order_id", "Unknown")
            response = {
                "status": "in_process",
                "message": f"Order {order_id} is currently being processed.",
                "last_updated": "2023-10-05",
                "expected_completion": "2023-10-20",
            }

        elif api_name == "branding_approval":
            # Logic for requesting or checking branding approval status.
            # Typically requires a "request_id" and possibly additional creative details.
            request_id = api_args.get("request_id", "N/A")
            response = {
                "status": "approved_with_remarks",
                "message": f"Branding request {request_id} has been approved with remarks.",
                "comments": "Please ensure all disclaimers and warnings are included.",
            }

        else:
            # Fallback for unrecognized API names.
            response = {
                "status": "failed",
                "message": "Invalid API name provided. No action taken.",
            }

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response)

        return response

class Settlement_api_callerTool(BaseTool):
    name: str = "settlement_api_caller"
    description: str = """This function routes calls to various internal services that replace CBOS operations.

Parameters:
-----------
api_name : str
    Name of the API to be invoked. Possible values include:
      1. "order_marketing_material"
         Used for placing or requesting marketing/branding collateral
         (e.g., flex boards, banners, visiting cards).
      2. "check_marketing_material_status"
         Used for inquiring about the status (within or beyond TAT) of any
         previously placed marketing material order.
      3. "branding_approval"
         Used for submitting or checking approvals regarding branding
         changes, logo updates, or regulatory disclaimers.

api_args : dict, optional
    Arguments relevant to the chosen API. For example:
      - "order_marketing_material" might expect:
          {
              "material_type": str,    # e.g., "flex", "banner", "visiting_card"
              "quantity": int,        # e.g., 10
              "branch_code": str,     # e.g., "RPRITIJAIN"
              "additional_notes": str # e.g., "Need updated logo version"
          }
      - "check_marketing_material_status" might expect:
          {
              "order_id": str         # e.g., "MAT12345"
          }
      - "branding_approval" might expect:
          {
              "request_id": str,      # e.g., "AYAC1200"
              "creative_details": str # e.g., "Updated disclaimers, warnings"
          }

Returns:
--------
dict
    A JSON-like response object with the outcome of the requested operation.
    The actual keys depend on the nature of the called API. Typical fields
    might include:
      - "status": Indicates success/failure or current processing state.
      - "message": Brief explanation or additional context.
      - Any other relevant information such as "order_id", "expected_delivery",
        "comments", or "last_updated".

Scenarios Covered (api_required = "Yes"):
-----------------------------------------
- Requesting new marketing material (scenario_ids: 603, 604, 605, 606, 607, 609,
  612, 613, 614, 615)
  => api_name = "order_marketing_material"
- Checking marketing material order status (scenario_ids: 608, 611, 616, etc.)
  => api_name = "check_marketing_material_status"
- Branding approval request (scenario_id: 610)
  => api_name = "branding_approval"""
    args_schema: Type[BaseModel] = Settlement_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return settlement_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return settlement_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

class Ekyc_api_callerInput(BaseModel):
    api_name: str = Field(..., description='Argument api_name')
    api_args: dict = Field(default={}, description='Argument api_args')

def ekyc_api_caller(api_name: str, api_args: dict = {},record_api_call:Optional[Callable]=None):
        """
        This function serves as a centralized controller to call various APIs that replace internal tool (CBOS, EKYC Utility, Saathi) access,
        directly required to resolve account opening and eKYC-related queries.

        Parameters:
        - api_name (str): The name of the API to call. Supported API names and descriptions:
            * "check_pan_existence":
                - Checks if a PAN number exists and returns its status (active/inactive/closed).
                - api_args: { "pan_number": str }
                - Returns: { "exists": bool, "status": str, "client_code": Optional[str] }
            * "get_ipv_master_status":
                - Fetches current IPV (In Person Verification) master record by IPV code or name.
                - api_args: { "ipv_code": Optional[str], "ipv_name": Optional[str] }
                - Returns: { "found": bool, "ipv_details": dict }
            * "check_ekyc_migration_status":
                - Checks status of eKYC account migration to CBOS.
                - api_args: { "client_code": str }
                - Returns: { "migrated": bool, "expected_completion_days": int }
            * "get_client_cbos_status":
                - Checks client status in CBOS using client code.
                - api_args: { "client_code": str }
                - Returns: { "status": str, "details": dict }
            * "get_ekyc_objection":
                - Retrieves any objections recorded for an eKYC client.
                - api_args: { "client_code": str }
                - Returns: { "objections": list }
            * "find_lead_in_saathi":
                - Checks for a lead presence in Saathi using mobile number.
                - api_args: { "mobile_number": str }
                - Returns: { "found": bool, "lead_id": Optional[str], "lead_status": Optional[str] }
            * "get_ekyc_details":
                - View the EKYC details for an identifier (PAN, mobile, email, Aadhaar).
                - api_args: { "pan": Optional[str], "mobile": Optional[str], "email": Optional[str], "aadhaar": Optional[str] }
                - Returns: { "found": bool, "ekyc_details": dict }
            * "lead_delete_status":
                - Shows the status of lead delete approval/rejection using the mobile number.
                - api_args: { "mobile_number": str }
                - Returns: { "lead_found": bool, "action_status": str }
        - api_args (dict, optional): Arguments needed by the selected API.

        Returns:
        - dict: Result object containing status/result fields as relevant for the called API.

        Note:
        This function stores the output in the `response` variable and returns it at the end as a dictionary.

        Example:
            api_caller("check_pan_existence", {"pan_number": "ABCDE1234F"})
        """

        response = {}

        if api_name == "check_pan_existence":
            pan_number = api_args.get("pan_number") if api_args else None
            # Simulating status check
            response = {
                "exists": True,
                "status": "active",  # possible: active, closed, inactive
                "client_code": "MO123456" if pan_number else None,
            }

        elif api_name == "get_ipv_master_status":
            ipv_code = api_args.get("ipv_code") if api_args else None
            ipv_name = api_args.get("ipv_name") if api_args else None
            # Simulating IPV master search
            response = {
                "found": bool(ipv_code or ipv_name),
                "ipv_details": (
                    {
                        "ipv_code": ipv_code or "IPV001",
                        "ipv_name": ipv_name or "John Doe",
                        "active": True,
                    }
                    if (ipv_code or ipv_name)
                    else None
                ),
            }

        elif api_name == "check_ekyc_migration_status":
            client_code = api_args.get("client_code") if api_args else None
            # Simulating migration status
            response = {"migrated": False, "expected_completion_days": 2}

        elif api_name == "get_client_cbos_status":
            client_code = api_args.get("client_code") if api_args else None
            # Simulating client status in CBOS
            response = {
                "status": "TBA",  # could be e.g. 'TBA', 'Active', 'Pending', etc.
                "details": {"kyc_status": "Pending", "activation_date": None},
            }

        elif api_name == "get_ekyc_objection":
            client_code = api_args.get("client_code") if api_args else None
            # Simulate fetching objections
            response = {
                "objections": [
                    {"code": "DOC_MISSING", "description": "PAN Document Missing"}
                ]
            }

        elif api_name == "find_lead_in_saathi":
            mobile_number = api_args.get("mobile_number") if api_args else None
            # Simulating lead lookup
            response = {
                "found": True,
                "lead_id": "LEAD20246678" if mobile_number else None,
                "lead_status": "Pending",
            }

        elif api_name == "get_ekyc_details":
            # At least one of the identifiers should be present
            ekyc_details = {"name": "Sample Name", "status": "Pending", "stage": "IPV Done"}
            response = {"found": True, "ekyc_details": ekyc_details}

        elif api_name == "lead_delete_status":
            mobile_number = api_args.get("mobile_number") if api_args else None
            response = {
                "lead_found": True if mobile_number else False,
                "action_status": "Approved" if mobile_number else "Not Found",
            }

        else:
            response = {"error": "Invalid API name or unsupported operation"}

        # api_tracker = APITracker.get_instance()
        # api_tracker.record_api_call(api_name, api_args, response)
        if callable(record_api_call):
            record_api_call(api_name, api_args, response)

        return response

class Ekyc_api_callerTool(BaseTool):
    name: str = "ekyc_api_caller"
    description: str = """This function serves as a centralized controller to call various APIs that replace internal tool (CBOS, EKYC Utility, Saathi) access,
directly required to resolve account opening and eKYC-related queries.

Parameters:
- api_name (str): The name of the API to call. Supported API names and descriptions:
    * "check_pan_existence":
        - Checks if a PAN number exists and returns its status (active/inactive/closed).
        - api_args: { "pan_number": str }
        - Returns: { "exists": bool, "status": str, "client_code": Optional[str] }
    * "get_ipv_master_status":
        - Fetches current IPV (In Person Verification) master record by IPV code or name.
        - api_args: { "ipv_code": Optional[str], "ipv_name": Optional[str] }
        - Returns: { "found": bool, "ipv_details": dict }
    * "check_ekyc_migration_status":
        - Checks status of eKYC account migration to CBOS.
        - api_args: { "client_code": str }
        - Returns: { "migrated": bool, "expected_completion_days": int }
    * "get_client_cbos_status":
        - Checks client status in CBOS using client code.
        - api_args: { "client_code": str }
        - Returns: { "status": str, "details": dict }
    * "get_ekyc_objection":
        - Retrieves any objections recorded for an eKYC client.
        - api_args: { "client_code": str }
        - Returns: { "objections": list }
    * "find_lead_in_saathi":
        - Checks for a lead presence in Saathi using mobile number.
        - api_args: { "mobile_number": str }
        - Returns: { "found": bool, "lead_id": Optional[str], "lead_status": Optional[str] }
    * "get_ekyc_details":
        - View the EKYC details for an identifier (PAN, mobile, email, Aadhaar).
        - api_args: { "pan": Optional[str], "mobile": Optional[str], "email": Optional[str], "aadhaar": Optional[str] }
        - Returns: { "found": bool, "ekyc_details": dict }
    * "lead_delete_status":
        - Shows the status of lead delete approval/rejection using the mobile number.
        - api_args: { "mobile_number": str }
        - Returns: { "lead_found": bool, "action_status": str }
- api_args (dict, optional): Arguments needed by the selected API.

Returns:
- dict: Result object containing status/result fields as relevant for the called API.

Note:
This function stores the output in the `response` variable and returns it at the end as a dictionary.

Example:
    api_caller("check_pan_existence", {"pan_number": "ABCDE1234F"})"""
    args_schema: Type[BaseModel] = Ekyc_api_callerInput
    

    async def _arun(self, api_name: str, api_args: Optional[dict] = None,run_manager: Optional[AsyncCallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return ekyc_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))

    def _run(self, api_name: str, api_args: Optional[dict]=None,run_manager: Optional[CallbackManagerForToolRun] = None):
        if api_args is None:
            api_args = {}
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        return ekyc_api_caller(api_name, api_args,self.metadata.get("record_api_call", None))


# ------------------------------------------------------------------------------------------------


import requests

bassurl=os.getenv("BASE_URL", "http://localhost:8000")

def generate_token(username):
    """Function to generate token for closure validation"""

    url = f"{bassurl}/closurevalidation/api/clsvalidation/generatetoken"
    
    headers = {"Content-Type": "application/json"}
    data = {"username": username}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()  # Assuming the response contains the token in JSON format
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    return None





def fetch_client_data(clientcode, token):
    """Function to fetch client data for closure validation"""
    # Input validation
    if not clientcode:
        return {
            "status": "failed",
            "message": "Client code is required.",
            "data": {}
        }
    
    if not token:
        return {
            "status": "failed",
            "message": "Authorization token is required.",
            "data": {}
        }
    

    url=f"{bassurl}/closurevalidation/api/clsvalidation/fetchdata"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {"clientcode": clientcode}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()  # Return the actual API response
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return {
            "status": "failed",
            "message": f"HTTP Error: {str(e)}",
            "data": {}
        }
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return {
            "status": "failed",
            "message": f"Request Error: {str(e)}",
            "data": {}
        }





class Closure_validation_fetch_data_toolInput(BaseModel):
    client_code: str = Field(..., description='Argument client_code')

def closure_validation_fetch_data_tool(client_code: str, record_api_call: Optional[Callable] = None) -> dict:
        """
        Description:
            Account closure validation


        Parameters:
            client_code (str):
        Returns:
            Dict:
                A JSON-compatible dictionary representing the result of the API call.
                The structure varies depending on the API called:
                   {
                     "status": "success",
                     "message": "Client closure validation data retrieved successfully.",
                "data": {
                       "ClientCode": "string",
                       "ReadyForClosure": "Y" or "N",
                       "LedgerBalance": number,
                       "InterestAccrued": number,
                       "PermanentAgeingDebit": number,
                       "DPHoldingValuation": number,
                       "MFSIPStatus": "Y" or "N",
                       "Remarks": "string"
                     },
                     "token_info": {
                       "status": "success",
                       "message": "Token generated successfully. Valid for 30 minutes."
                     }
                   }
        """



        if not client_code:
            response = {
                "status": "Failed",
                "message": "Client code is required",
                "data": {},
            }
        else:
            # Step 1: Generate token
            token_response = generate_token("TOKEN")

            # Step 2: If token generation successful, fetch client data
            if token_response:

                client_response = fetch_client_data(client_code, token_response)

                # Combine the responses
                if (
                    client_response
                    and client_response.get("Table")
                    and len(client_response["Table"]) > 0
                    and client_response["Table"][0].get("ReadyForClosure") == "N"
                ):
                    response = {
                        "status": "Failed",
                        "message": "Client is not ready for closure",
                        "data": (
                            client_response["Table"][0]
                            if client_response.get("Table")
                            else {}
                        ),
                    }
                elif (
                    client_response
                    and client_response.get("Table")
                    and len(client_response["Table"]) > 0
                    and client_response["Table"][0].get("ReadyForClosure") == "Y"
                ):
                    response = {
                        "status": "success",
                        "message": "Client is ready for closure",
                        "data": (
                            client_response["Table"][0]
                            if client_response.get("Table")
                            else {}
                        ),
                    }
                else:
                    response = {
                        "status": "Failed",
                        "message": "Client is not ready for closure",
                        "data": (
                            client_response["Table"][0]
                            if client_response.get("Table")
                            else {}
                        ),
                    }
            else:
                response = {
                    "status": "Failed",
                    "message": "Failed to generate token",
                    "data": {},
                }
        if callable(record_api_call):
            record_api_call("closure_validation_fetch_data", {
                "client_code": client_code
            }, response)
    
        return response

class Closure_validation_fetch_data_toolTool(BaseTool):
    name: str = "closure_validation_fetch_data_tool"
    description: str = """Description:
    Account closure validation


Parameters:
    client_code (str):
Returns:
    Dict:
        A JSON-compatible dictionary representing the result of the API call.
        The structure varies depending on the API called:
           {
             "status": "success",
             "message": "Client closure validation data retrieved successfully.",
             "data": {
               "ClientCode": "string",
               "ReadyForClosure": "Y" or "N",
               "LedgerBalance": number,
               "InterestAccrued": number,
               "PermanentAgeingDebit": number,
               "DPHoldingValuation": number,
               "MFSIPStatus": "Y" or "N",
               "Remarks": "string"
             },
             "token_info": {
               "status": "success",
               "message": "Token generated successfully. Valid for 30 minutes."
             }
           }"""
    args_schema: Type[BaseModel] = Closure_validation_fetch_data_toolInput

    async def _arun(self, client_code:str,):
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        
        return closure_validation_fetch_data_tool(client_code, self.metadata.get("record_api_call", None))

    def _run(self, client_code:str):
        if self.metadata is None:
          raise ValueError("Metadata is not provided")
        
        return closure_validation_fetch_data_tool(client_code, self.metadata.get("record_api_call", None))
          
    
        
		
