"""An AWS Python Pulumi program"""

import pulumi
from pulumi_aws import s3
from autotag import register_auto_tags
import pulumi_aws as aws

register_auto_tags({
    'user:Project': pulumi.get_project(),
    'user:Stack': pulumi.get_stack(),
    'application': 'test',
    'cost-center': 390,
    #'data-center': aws.get_region().name,
    'environment': pulumi.get_stack(),
    'product': 'policy',
    'product-area': 'devsecops',
    'backup-by': 'N/A',
    'delete-after': 'N/A',
})

# Create an AWS resource (S3 Bucket)
bucket = s3.Bucket('my-bucket')

# Export the name of the bucket
pulumi.export('bucket_name', bucket.id)
