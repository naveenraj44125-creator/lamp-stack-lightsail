# Lightsail Bucket Integration Guide

## Overview

This LAMP stack application is integrated with AWS Lightsail buckets for object storage. The bucket is automatically created and attached to your instance during deployment.

## Configuration

The bucket is configured in `deployment-lamp-stack.config.yml`:

```yaml
lightsail:
  bucket:
    enabled: true
    name: "lamp-stack-demo-bucket"
    access_level: "read_write"  # or "read_only"
    bundle_id: "small_1_0"      # small_1_0, medium_1_0, large_1_0
```

### Bucket Sizes

- **small_1_0**: 250GB storage, 100GB transfer/month
- **medium_1_0**: 500GB storage, 250GB transfer/month
- **large_1_0**: 1TB storage, 500GB transfer/month

### Access Levels

- **read_only**: Instance can download from bucket
- **read_write**: Instance can upload and download

## Automatic Setup

During deployment, the system automatically:

1. ✅ Creates the bucket if it doesn't exist
2. ✅ Attaches the bucket to your instance
3. ✅ Configures access permissions
4. ✅ Sets up AWS credentials via instance role

## Usage Examples

### 1. AWS CLI

The AWS CLI is pre-installed on your instance:

```bash
# List bucket contents
aws s3 ls s3://lamp-stack-demo-bucket/

# Upload a file
aws s3 cp myfile.txt s3://lamp-stack-demo-bucket/

# Download a file
aws s3 cp s3://lamp-stack-demo-bucket/myfile.txt ./

# Sync directory
aws s3 sync ./uploads/ s3://lamp-stack-demo-bucket/uploads/

# Delete a file
aws s3 rm s3://lamp-stack-demo-bucket/myfile.txt
```

### 2. PHP with AWS SDK

First, install the AWS SDK:

```bash
composer require aws/aws-sdk-php
```

Then use it in your PHP code:

```php
<?php
require 'vendor/autoload.php';

use Aws\S3\S3Client;

// Create S3 client (credentials from instance role)
$s3 = new S3Client([
    'version' => 'latest',
    'region'  => 'us-east-1'
]);

// Upload file
$s3->putObject([
    'Bucket' => 'lamp-stack-demo-bucket',
    'Key'    => 'uploads/photo.jpg',
    'Body'   => fopen('/path/to/photo.jpg', 'r'),
    'ACL'    => 'private'
]);

// Download file
$result = $s3->getObject([
    'Bucket' => 'lamp-stack-demo-bucket',
    'Key'    => 'uploads/photo.jpg'
]);

file_put_contents('/path/to/save.jpg', $result['Body']);

// List objects
$result = $s3->listObjects([
    'Bucket' => 'lamp-stack-demo-bucket',
    'Prefix' => 'uploads/'
]);

foreach ($result['Contents'] as $object) {
    echo $object['Key'] . "\n";
}

// Delete object
$s3->deleteObject([
    'Bucket' => 'lamp-stack-demo-bucket',
    'Key'    => 'uploads/photo.jpg'
]);
?>
```

### 3. File Upload Example

Here's a complete example for handling file uploads:

```php
<?php
require 'vendor/autoload.php';

use Aws\S3\S3Client;

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['file'])) {
    $s3 = new S3Client([
        'version' => 'latest',
        'region'  => 'us-east-1'
    ]);
    
    $file = $_FILES['file'];
    $fileName = basename($file['name']);
    $filePath = $file['tmp_name'];
    
    try {
        // Upload to bucket
        $result = $s3->putObject([
            'Bucket' => 'lamp-stack-demo-bucket',
            'Key'    => 'uploads/' . $fileName,
            'Body'   => fopen($filePath, 'r'),
            'ACL'    => 'private',
            'ContentType' => $file['type']
        ]);
        
        echo "✅ File uploaded successfully!";
        echo "URL: " . $result['ObjectURL'];
        
    } catch (Exception $e) {
        echo "❌ Upload failed: " . $e->getMessage();
    }
}
?>

<form method="POST" enctype="multipart/form-data">
    <input type="file" name="file" required>
    <button type="submit">Upload to Bucket</button>
</form>
```

## Common Use Cases

### 1. User File Uploads

Store user-uploaded files (images, documents, etc.) in the bucket instead of local storage:

```php
// Upload user avatar
$s3->putObject([
    'Bucket' => 'lamp-stack-demo-bucket',
    'Key'    => 'avatars/' . $userId . '.jpg',
    'Body'   => fopen($avatarFile, 'r')
]);
```

### 2. Database Backups

Automatically backup your database to the bucket:

```bash
#!/bin/bash
# Backup PostgreSQL database
pg_dump -U $DB_USER $DB_NAME | gzip > backup.sql.gz

# Upload to bucket
aws s3 cp backup.sql.gz s3://lamp-stack-demo-bucket/backups/$(date +%Y%m%d).sql.gz

# Clean up
rm backup.sql.gz
```

### 3. Static Asset Storage

Serve static assets (CSS, JS, images) from the bucket:

```php
// Generate presigned URL for private files
$cmd = $s3->getCommand('GetObject', [
    'Bucket' => 'lamp-stack-demo-bucket',
    'Key'    => 'private/document.pdf'
]);

$request = $s3->createPresignedRequest($cmd, '+20 minutes');
$presignedUrl = (string) $request->getUri();

echo "<a href='$presignedUrl'>Download Document</a>";
```

### 4. Log Archival

Archive application logs to the bucket:

```bash
# Compress and upload logs
tar -czf logs-$(date +%Y%m%d).tar.gz /var/log/apache2/
aws s3 cp logs-$(date +%Y%m%d).tar.gz s3://lamp-stack-demo-bucket/logs/
```

## Security Best Practices

1. **Never store credentials in code** - Use instance role (automatic)
2. **Validate file uploads** - Check file types and sizes
3. **Set appropriate ACLs** - Use 'private' for sensitive data
4. **Use presigned URLs** - For temporary access to private files
5. **Enable encryption** - For sensitive data at rest
6. **Implement virus scanning** - For user uploads
7. **Set lifecycle policies** - To automatically delete old files

## Troubleshooting

### Check bucket status

```bash
# List buckets
aws lightsail get-buckets

# Get specific bucket info
aws lightsail get-buckets --bucket-name lamp-stack-demo-bucket

# Check instance access
aws lightsail get-bucket-access-keys --bucket-name lamp-stack-demo-bucket
```

### Test bucket access

```bash
# Test write access
echo "test" > test.txt
aws s3 cp test.txt s3://lamp-stack-demo-bucket/test.txt

# Test read access
aws s3 cp s3://lamp-stack-demo-bucket/test.txt ./test-download.txt

# Clean up
aws s3 rm s3://lamp-stack-demo-bucket/test.txt
rm test.txt test-download.txt
```

### Common Issues

**Issue**: "Access Denied" errors
- **Solution**: Check that bucket is attached to instance with correct access level

**Issue**: "Bucket not found"
- **Solution**: Verify bucket name in config matches actual bucket name

**Issue**: "Credentials not found"
- **Solution**: Ensure instance has proper IAM role attached

## Demo Page

Visit `/bucket-demo.php` on your deployed application to see:
- Bucket configuration details
- Usage examples
- Installation instructions
- Common use cases

## Additional Resources

- [AWS SDK for PHP Documentation](https://docs.aws.amazon.com/sdk-for-php/)
- [AWS CLI S3 Commands](https://docs.aws.amazon.com/cli/latest/reference/s3/)
- [Lightsail Buckets Documentation](https://lightsail.aws.amazon.com/ls/docs/en_us/articles/amazon-lightsail-buckets)
- [S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/best-practices.html)
