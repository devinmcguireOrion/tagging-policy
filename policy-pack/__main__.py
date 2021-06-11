from pulumi_policy import (
    EnforcementLevel,
    PolicyPack,
    ReportViolation,
    ResourceValidationArgs,
    ResourceValidationPolicy,
)
from taggable import is_taggable
import datetime

requiredTags = ["application", "cost-center", "delete-after", "environment", "product", "product-area"]
tagDerivatives = {
    'application' : ['app'], 
    'environment' : ['env']
}
timeTags = ["backup-by"] #Only for EC2/EBS
environmentValues = ["sandbox", "dev", "test", "staging", "alpha", "alpha2", "prod"]


def has_tags_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    if is_taggable(args.resource_type):
        if 'tags' not in args.props:
            report_violation(
                f"Resource does not have any tags")

def check_for_required_tags_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    if is_taggable(args.resource_type):
        if 'tags' in args.props:
            # list of all the resource's tags
            tags = list(args.props['tags'].keys())
            # create a lower case copy to ignore capitalization
            lowerTags = [x.lower() for x in tags]
            # check if a proper tag is missing before looking for derivatives
            for rt in requiredTags:
                if rt not in tags:
                    if rt in tagDerivatives:
                        # search each tag individually to see if they contain a derivative of the tag name
                        derivFound = False
                        for lowerTag in lowerTags:
                            for deriv in tagDerivatives[rt]:
                                if deriv in lowerTag:
                                    #use the lower case index to return the proper capitalization of the false tag
                                    tag = tags[lowerTags.index(lowerTag)]
                                    derivFound = True
                                    report_violation(
                                        f"Please use tag name '{rt}' instead of '{tag}'")
                        if not derivFound:
                            report_violation(
                                f"Resource is missing required tag '{rt}'")
                    else:
                        report_violation(
                            f"Resource is missing required tag '{rt}'")

def check_for_environment_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    if is_taggable(args.resource_type):
        if 'tags' in args.props:
            tags = args.props['tags']
            if "environment" in tags:
                if tags["environment"] not in environmentValues:
                    report_violation(
                        f"'{tags['environment']}' is an invalid environment value. Proper values include {environmentValues}")

def check_for_time_tags_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    if is_taggable(args.resource_type):
        if "ebs" in args.resource_type or "ec2" in args.resource_type:
            if 'tags' in args.props:
                tags = args.props['tags']
                for rt in timeTags:
                    if rt not in tags:
                        report_violation(
                            f"Resource is missing required tag '{rt}'")


check_for_tags = ResourceValidationPolicy(
    name="check-for-tags",
    description="Validates tags on taggable AWS resources.",
    enforcement_level=EnforcementLevel.ADVISORY,
    validate=[
        has_tags_validator, 
        check_for_required_tags_validator,
        check_for_time_tags_validator,
        check_for_environment_validator,
    ]
)

PolicyPack(
    name="tagging-policy",
    policies=[
        check_for_tags,
    ],
)