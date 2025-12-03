<?php
/**
 * S3 Bucket File Download Handler
 * Downloads files from S3 bucket and serves them to the user
 */

// Bucket configuration
$bucketName = getenv('BUCKET_NAME') ?: 'lamp-stack-demo-bucket';

// Get file key from query parameter
$fileKey = $_GET['key'] ?? '';

if (empty($fileKey)) {
    die('Error: No file specified');
}

// Check if AWS CLI is available
$awsCliAvailable = !empty(shell_exec('which aws 2>/dev/null'));

if (!$awsCliAvailable) {
    die('Error: AWS CLI is not installed');
}

// Create temporary file
$tmpFile = tempnam(sys_get_temp_dir(), 's3_download_');

// Download from S3
$command = sprintf(
    'aws s3 cp s3://%s/%s %s 2>&1',
    escapeshellarg($bucketName),
    escapeshellarg($fileKey),
    escapeshellarg($tmpFile)
);

$output = shell_exec($command);

// Check if download was successful
if (!file_exists($tmpFile) || filesize($tmpFile) === 0) {
    unlink($tmpFile);
    die('Error downloading file: ' . htmlspecialchars($output));
}

// Get filename
$fileName = basename($fileKey);

// Determine content type
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$mimeType = finfo_file($finfo, $tmpFile);
finfo_close($finfo);

// Set headers for download
header('Content-Type: ' . $mimeType);
header('Content-Disposition: attachment; filename="' . $fileName . '"');
header('Content-Length: ' . filesize($tmpFile));
header('Cache-Control: no-cache, must-revalidate');
header('Pragma: no-cache');

// Output file
readfile($tmpFile);

// Clean up
unlink($tmpFile);
exit;
