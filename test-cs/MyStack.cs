using Pulumi;
using Pulumi.Aws.S3;
using Aws = Pulumi.Aws;
using System.Threading.Tasks;

class MyStack : Stack
{
    public MyStack()
    {
        // Create an AWS resource (S3 Bucket)
        var bucket = new Bucket("my-bucket", new BucketArgs {
                Tags = {
                    { "data-center", Output.Create(Aws.GetRegion.InvokeAsync().Result.Name) },
                },});

        // Export the name of the bucket
        this.BucketName = bucket.Id;
    }


    [Output]
    public Output<string> BucketName { get; set; }
}
