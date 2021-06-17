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
                    { "data-center", Output.Create(Aws.GetRegion.InvokeAsync()) },
                },});

        // Export the name of the bucket
        this.BucketName = bucket.Id;
    }

    public static class GetRegion {
        public static Task<Aws.GetRegionResult> InvokeAsync(Aws.GetRegionArgs args, InvokeOptions? opts = null){

        }
    }

    [Output]
    public Output<string> BucketName { get; set; }
}
