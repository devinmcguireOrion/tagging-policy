from pulumi_policy import (
    EnforcementLevel,
    PolicyPack,
    ReportViolation,
    ResourceValidationArgs,
    ResourceValidationPolicy,
)
import pulumi_policy
from taggable import is_taggable
import datetime

requiredTags = ["application", "cost-center", "data-center", "delete-after", "environment", "product", "product-area"]
tagDerivatives = {
    'application' : ['app'], 
    'environment' : ['env'],
    #'product' : ['proj'],
}
timeTags = ["backup-by"] #Only for EC2/EBS
environmentValues = ["sandbox", "dev", "test", "staging", "alpha", "alpha2", "prod"]

def has_tags_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    try:
        if is_taggable(args.resource_type):
            if 'tags' not in args.props:
                report_violation(
                    f"Resource '{args.urn}' does not have any tags")
    except Exception as e:
        report_violation(
            f"Exception calling application: {e}")

def check_for_required_tags_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    try:
        if is_taggable(args.resource_type):
            if 'tags' in args.props:
                # list of all the resource's tags
                if type(args.props['tags']) == pulumi_policy.proxy._DictProxy:
                    tags = list(args.props['tags'].keys())    
                elif type(args.props['tags']) == pulumi_policy.proxy._ListProxy:
                    tags = []
                    for i in args.props['tags']:
                        if type(i) == pulumi_policy.proxy._DictProxy and 'key' in i:
                            tags.append(i['key'])
                else:
                    report_violation(
                        f"Tags are of type '{type(args.props['tags'])}' on resource '{args.urn}' and were not checked.")
                    return
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
                                        # use the lower case index to return the proper capitalization of the false tag
                                        tag = tags[lowerTags.index(lowerTag)]
                                        derivFound = True
                                        report_violation(
                                            f"Please use tag name '{rt}' instead of '{tag}' on resource '{args.urn}'")
                            if not derivFound:
                                report_violation(
                                    f"Resource '{args.urn}' is missing required tag '{rt}'")
                        else:
                            # missing tag has no derivatives
                            report_violation(
                                f"Resource '{args.urn}' is missing required tag '{rt}'")
                    elif rt in tagDerivatives:
                        # look for tags with different names that probably represent the same thing
                        derivFound = False
                        for lowerTag in lowerTags:
                            for deriv in tagDerivatives[rt]:
                                if deriv in lowerTag:
                                    tag = tags[lowerTags.index(lowerTag)]
                                    derivFound = True
                                    if tag not in requiredTags:
                                        report_violation(
                                                f"Tag '{tag}' is redundant. Please just use '{rt}' on resource '{args.urn}'")
    except Exception as e:
        report_violation(
            f"Exception calling application: {e}")


def check_for_time_tags_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    try:
        if is_taggable(args.resource_type):
            if "ebs" in args.resource_type or "ec2" in args.resource_type:
                if 'tags' in args.props:
                    tags = args.props['tags']
                    for rt in timeTags:
                        if rt not in tags:
                            report_violation(
                                f"Resource '{args.urn}' is missing required tag '{rt}'")
    except Exception as e:
        report_violation(
            f"Exception calling application: {e}")

def check_backup_value_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    try:
        if is_taggable(args.resource_type):
            if 'tags' in args.props:
                tags = args.props['tags']
                if "backup-by" in tags:
                    if type(tags["backup-by"]) != datetime:
                        report_violation(
                            f"'{tags['backup-by']}' is an invalid backup-by value on resource '{args.urn}'. Proper value must be a datetime in YYYY/MM/DD format")
    except Exception as e:
        report_violation(
            f"Exception calling application: {e}")

def check_delete_value_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    try:
        if is_taggable(args.resource_type):
            if 'tags' in args.props:
                tags = args.props['tags']
                if "delete-after" in tags:
                    if type(tags["delete-after"]) != datetime or tags["delete-after"] != "Never":
                        report_violation(
                            f"'{tags['delete-after']}' is an invalid delete-after value on resource '{args.urn}'. Proper value must be a datetime in YYYY/MM/DD format or a string with the value 'Never'")
    except Exception as e:
        report_violation(
            f"Exception calling application: {e}")

def check_environment_value_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    try:
        if is_taggable(args.resource_type):
            if 'tags' in args.props:
                tags = args.props['tags']
                if "environment" in tags:
                    if tags["environment"] not in environmentValues:
                        report_violation(
                            f"'{tags['environment']}' is an invalid environment value on resource '{args.urn}'. Proper values include {environmentValues}")
    except Exception as e:
        report_violation(
            f"Exception calling application: {e}")

check_for_tags = ResourceValidationPolicy(
    name="check-for-tags",
    description="Validates tags on taggable AWS resources.",
    enforcement_level=EnforcementLevel.ADVISORY,
    validate=[
        has_tags_validator, 
        check_for_required_tags_validator,
        check_for_time_tags_validator,
        #check_backup_value_validator,
        #check_delete_value_validator,
        check_environment_value_validator,
    ]
)

PolicyPack(
    name="tagging-policy",
    policies=[
        check_for_tags,
    ],
)