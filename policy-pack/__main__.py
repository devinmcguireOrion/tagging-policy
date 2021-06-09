from pulumi_policy import (
    EnforcementLevel,
    PolicyPack,
    ReportViolation,
    ResourceValidationArgs,
    ResourceValidationPolicy,
)
from taggable import is_taggable

requiredTags = ["application","backup-by","cost-center","delete-after","environment","product","product-area"]

def check_for_tags_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    if is_taggable(args.resource_type):
        ts = args.props['tags']
        for rt in requiredTags:
            if rt not in ts:
                report_violation(
                    f"Taggable resource '{args.urn}' is missing required tag '{rt}'")

check_for_tags = ResourceValidationPolicy(
    name="check-required-tags",
    description="Looks for specified tags on each resource.",
    enforcement_level=EnforcementLevel.ADVISORY,
    validate=check_for_tags_validator,
)

PolicyPack(
    name="tagging-policy",
    policies=[
        check_for_tags,
    ],
)
