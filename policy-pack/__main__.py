from pulumi_policy import (
    EnforcementLevel,
    PolicyPack,
    ReportViolation,
    ResourceValidationArgs,
    ResourceValidationPolicy,
)
from taggable import is_taggable

requiredTags = ["application", "cost-center", "environment", "product", "product-area"]
timeTags = ["backup-by","delete-after"] #Should auto-tag check if ec2 or ebs?
stackTags = ["project", "stack"]

def has_tags_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    if is_taggable(args.resource_type):
        if 'tags' not in args.props:
            report_violation(
                f"Taggable resource '{args.urn}' does not have any tags")

def check_for_required_tags_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    if is_taggable(args.resource_type):
        if 'tags' in args.props:
            ts = args.props['tags']
            for rt in requiredTags:
                if rt not in ts:
                    report_violation(
                        f"Taggable resource '{args.urn}' is missing required tag '{rt}'")

def check_for_time_tags_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    if is_taggable(args.resource_type):
        if "ebs" in args.resource_type or "ec2" in args.resource_type:
            if 'tags' in args.props:
                ts = args.props['tags']
                for rt in timeTags:
                    if rt not in ts:
                        report_violation(
                            f"Taggable resource '{args.urn}' is missing required tag '{rt}'")

def check_for_stack_tags_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    if is_taggable(args.resource_type):
        if 'tags' in args.props:
            ts = args.props['tags']
            for rt in stackTags:
                if rt not in ts:
                    report_violation(
                        f"Taggable resource '{args.urn}' is missing required tag '{rt}'")

check_for_tags = ResourceValidationPolicy(
    name="check-for-tags",
    description="Looks for tags on taggable resources.",
    enforcement_level=EnforcementLevel.ADVISORY,
    validate=[
        has_tags_validator, 
        check_for_required_tags_validator, 
        #check_for_stack_tags_validator, 
        check_for_time_tags_validator,
    ]
)

PolicyPack(
    name="tagging-policy",
    policies=[
        check_for_tags,
    ],
)