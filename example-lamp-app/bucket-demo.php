<?php
/**
 * Lightsail Bucket Demo
 * 
 * This file demonstrates how to use AWS S3 SDK with Lightsail buckets
 * The bucket is automatically attached to the instance with credentials
 */

// Bucket configuration from environment or config
$bucketName = getenv('BUCKET_NAME') ?: 'lamp-stack-demo-bucket';
$bucketRegion = getenv('AWS_REGION') ?: 'us-east-1';

// Check if AWS SDK is available
$awsSdkAvailable = class_exists('Aws\S3\S3Client');

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lightsail Bucket Demo</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🪣 Lightsail Bucket Demo</h1>
        </header>
        
        <main>
            <div class="info-section">
                <h3>Bucket Configuration</h3>
                <ul>
                    <li><strong>Bucket Name:</strong> <?php echo htmlspecialchars($bucketName); ?></li>
                    <li><strong>Region:</strong> <?php echo htmlspecialchars($bucketRegion); ?></li>
                    <li><strong>AWS SDK:</strong> <?php echo $awsSdkAvailable ? '✅ Available' : '⚠️ Not installed'; ?></li>
                </ul>
            </div>

            <div class="info-section">
                <h3>📚 Usage Examples</h3>
                
                <h4>1. Using AWS CLI</h4>
                <pre><code># List bucket contents
aws s3 ls s3://<?php echo $bucketName; ?>/

# Upload a file
aws s3 cp myfile.txt s3://<?php echo $bucketName; ?>/

# Download a file
aws s3 cp s3://<?php echo $bucketName; ?>/myfile.txt ./

# Sync directory
aws s3 sync ./uploads/ s3://<?php echo $bucketName; ?>/uploads/</code></pre>

                <h4>2. Using PHP with AWS SDK</h4>
                <pre><code>&lt;?php
require 'vendor/autoload.php';

use Aws\S3\S3Client;

// Create S3 client (credentials from instance role)
$s3 = new S3Client([
    'version' => 'latest',
    'region'  => '<?php echo $bucketRegion; ?>'
]);

// List objects
$result = $s3->listObjects([
    'Bucket' => '<?php echo $bucketName; ?>'
]);

foreach ($result['Contents'] as $object) {
    echo $object['Key'] . "\n";
}

// Upload file
$s3->putObject([
    'Bucket' => '<?php echo $bucketName; ?>',
    'Key'    => 'uploads/myfile.txt',
    'Body'   => fopen('/path/to/file.txt', 'r'),
    'ACL'    => 'private'
]);

// Download file
$result = $s3->getObject([
    'Bucket' => '<?php echo $bucketName; ?>',
    'Key'    => 'uploads/myfile.txt'
]);

file_put_contents('/path/to/save.txt', $result['Body']);
?&gt;</code></pre>

                <h4>3. Using cURL (Direct S3 API)</h4>
                <pre><code># Get temporary credentials from instance metadata
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
CREDS=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/)

# Use credentials with S3 API
# (Requires AWS Signature Version 4 signing)</code></pre>
            </div>

            <div class="info-section">
                <h3>🔧 Installation Instructions</h3>
                
                <h4>Install AWS SDK for PHP</h4>
                <pre><code># Using Composer
composer require aws/aws-sdk-php

# Or download manually
wget https://docs.aws.amazon.com/aws-sdk-php/v3/download/aws.phar</code></pre>

                <h4>Install AWS CLI (if not already installed)</h4>
                <pre><code># On Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y awscli

# Or using pip
pip3 install awscli</code></pre>
            </div>

            <div class="info-section">
                <h3>💡 Common Use Cases</h3>
                <ul>
                    <li><strong>File Uploads:</strong> Store user-uploaded files (images, documents, etc.)</li>
                    <li><strong>Static Assets:</strong> Serve CSS, JS, images from bucket</li>
                    <li><strong>Backups:</strong> Store database backups and application snapshots</li>
                    <li><strong>Logs:</strong> Archive application and server logs</li>
                    <li><strong>Media Storage:</strong> Store videos, audio files, large media</li>
                    <li><strong>Data Export:</strong> Store generated reports and exports</li>
                </ul>
            </div>

            <div class="info-section">
                <h3>🔐 Security Notes</h3>
                <ul>
                    <li>✅ Credentials are automatically provided via instance role</li>
                    <li>✅ No need to store access keys in code or config files</li>
                    <li>✅ Access level is controlled by bucket attachment (read-only or read-write)</li>
                    <li>⚠️ Always validate and sanitize file uploads</li>
                    <li>⚠️ Set appropriate ACLs on uploaded objects</li>
                    <li>⚠️ Consider encryption for sensitive data</li>
                </ul>
            </div>

            <div style="text-align: center; margin-top: 30px;">
                <a href="index.php" class="btn btn-primary">← Back to Main Page</a>
            </div>
        </main>
        
        <footer>
            <p>&copy; 2025 Lightsail Bucket Demo</p>
        </footer>
    </div>
</body>
</html>
