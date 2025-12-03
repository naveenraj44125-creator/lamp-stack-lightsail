<?php
// AWS Lightsail Bucket Helper Functions

function getBucketConfig() {
    return [
        'bucket_name' => getenv('BUCKET_NAME') ?: 'recipe-images-bucket',
        'region' => getenv('AWS_REGION') ?: 'us-east-1',
        'prefix' => 'recipes/'
    ];
}

function uploadImageToBucket($file, $filename) {
    $config = getBucketConfig();
    $bucket = $config['bucket_name'];
    $region = $config['region'];
    $key = $config['prefix'] . $filename;
    
    // Use AWS CLI to upload (IAM role provides credentials automatically)
    $tempFile = $file['tmp_name'];
    $contentType = $file['type'];
    
    $command = sprintf(
        'aws s3 cp %s s3://%s/%s --region %s --content-type %s 2>&1',
        escapeshellarg($tempFile),
        escapeshellarg($bucket),
        escapeshellarg($key),
        escapeshellarg($region),
        escapeshellarg($contentType)
    );
    
    exec($command, $output, $returnCode);
    
    if ($returnCode === 0) {
        return [
            'success' => true,
            'key' => $key,
            'url' => getImageUrl($key)
        ];
    }
    
    error_log("S3 upload failed: " . implode("\n", $output));
    return [
        'success' => false,
        'error' => 'Failed to upload image to bucket'
    ];
}

function getImageUrl($key) {
    $config = getBucketConfig();
    $bucket = $config['bucket_name'];
    $region = $config['region'];
    
    // Generate public URL
    return "https://{$bucket}.{$region}.amazonaws.com/{$key}";
}

function deleteImageFromBucket($key) {
    $config = getBucketConfig();
    $bucket = $config['bucket_name'];
    $region = $config['region'];
    
    $command = sprintf(
        'aws s3 rm s3://%s/%s --region %s 2>&1',
        escapeshellarg($bucket),
        escapeshellarg($key),
        escapeshellarg($region)
    );
    
    exec($command, $output, $returnCode);
    
    return $returnCode === 0;
}

function testBucketConnection() {
    $config = getBucketConfig();
    $bucket = $config['bucket_name'];
    $region = $config['region'];
    
    $command = sprintf(
        'aws s3 ls s3://%s --region %s 2>&1',
        escapeshellarg($bucket),
        escapeshellarg($region)
    );
    
    exec($command, $output, $returnCode);
    
    return $returnCode === 0;
}

function generateUniqueFilename($originalFilename) {
    $extension = pathinfo($originalFilename, PATHINFO_EXTENSION);
    return uniqid('recipe_', true) . '.' . strtolower($extension);
}

function validateImageFile($file) {
    $allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    $maxSize = getenv('UPLOAD_MAX_SIZE') ?: 5242880; // 5MB default
    
    if (!in_array($file['type'], $allowedTypes)) {
        return ['valid' => false, 'error' => 'Invalid file type. Only JPG, PNG, GIF, and WebP allowed.'];
    }
    
    if ($file['size'] > $maxSize) {
        return ['valid' => false, 'error' => 'File too large. Maximum size: ' . ($maxSize / 1024 / 1024) . 'MB'];
    }
    
    if ($file['error'] !== UPLOAD_ERR_OK) {
        return ['valid' => false, 'error' => 'Upload error occurred'];
    }
    
    return ['valid' => true];
}
