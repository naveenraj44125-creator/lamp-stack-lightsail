<?php
/**
 * Lightsail Bucket Manager - Working Upload/Download Interface
 * Uses AWS CLI for S3 operations (no SDK required)
 */

// Bucket configuration
$bucketName = getenv('BUCKET_NAME') ?: 'lamp-stack-demo-bucket';
$bucketRegion = getenv('AWS_REGION') ?: 'us-east-1';

$message = '';
$error = '';
$files = [];

// Check if AWS CLI is available
$awsCliAvailable = !empty(shell_exec('which aws 2>/dev/null'));

// Handle file upload
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action'])) {
    if (!$awsCliAvailable) {
        $error = "❌ AWS CLI is not installed on this server";
    } else {
        switch ($_POST['action']) {
            case 'upload':
                if (isset($_FILES['file']) && $_FILES['file']['error'] === UPLOAD_ERR_OK) {
                    $tmpFile = $_FILES['file']['tmp_name'];
                    $fileName = basename($_FILES['file']['name']);
                    $s3Key = 'uploads/' . date('Y-m-d') . '/' . $fileName;
                    
                    // Upload to S3 using AWS CLI
                    $command = sprintf(
                        'aws s3 cp %s s3://%s/%s 2>&1',
                        escapeshellarg($tmpFile),
                        escapeshellarg($bucketName),
                        escapeshellarg($s3Key)
                    );
                    
                    $output = shell_exec($command);
                    
                    if (strpos($output, 'upload:') !== false) {
                        $message = "✅ File uploaded successfully: $fileName";
                    } else {
                        $error = "❌ Upload failed: " . htmlspecialchars($output);
                    }
                } else {
                    $error = "❌ No file selected or upload error";
                }
                break;
                
            case 'delete':
                if (isset($_POST['file_key'])) {
                    $fileKey = $_POST['file_key'];
                    
                    $command = sprintf(
                        'aws s3 rm s3://%s/%s 2>&1',
                        escapeshellarg($bucketName),
                        escapeshellarg($fileKey)
                    );
                    
                    $output = shell_exec($command);
                    
                    if (strpos($output, 'delete:') !== false) {
                        $message = "✅ File deleted successfully";
                    } else {
                        $error = "❌ Delete failed: " . htmlspecialchars($output);
                    }
                }
                break;
                
            case 'test_connection':
                // Test bucket access
                $command = sprintf(
                    'aws s3 ls s3://%s/ 2>&1',
                    escapeshellarg($bucketName)
                );
                
                $output = shell_exec($command);
                
                if (strpos($output, 'An error occurred') === false && strpos($output, 'NoSuchBucket') === false) {
                    $message = "✅ Bucket connection successful!";
                } else {
                    $error = "❌ Bucket connection failed: " . htmlspecialchars($output);
                }
                break;
        }
    }
}

// List files in bucket
if ($awsCliAvailable) {
    $command = sprintf(
        'aws s3 ls s3://%s/ --recursive 2>&1',
        escapeshellarg($bucketName)
    );
    
    $output = shell_exec($command);
    
    if ($output && strpos($output, 'An error occurred') === false) {
        $lines = explode("\n", trim($output));
        foreach ($lines as $line) {
            if (preg_match('/^(\S+\s+\S+)\s+(\d+)\s+(.+)$/', $line, $matches)) {
                $files[] = [
                    'date' => $matches[1],
                    'size' => $matches[2],
                    'key' => $matches[3]
                ];
            }
        }
    }
}

// Function to format file size
function formatBytes($bytes) {
    if ($bytes >= 1073741824) {
        return number_format($bytes / 1073741824, 2) . ' GB';
    } elseif ($bytes >= 1048576) {
        return number_format($bytes / 1048576, 2) . ' MB';
    } elseif ($bytes >= 1024) {
        return number_format($bytes / 1024, 2) . ' KB';
    } else {
        return $bytes . ' bytes';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>S3 Bucket Manager</title>
    <link rel="stylesheet" href="css/style.css">
    <style>
        .file-list {
            margin: 20px 0;
        }
        .file-item {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .file-info {
            flex: 1;
        }
        .file-name {
            font-weight: bold;
            color: #2563eb;
            margin-bottom: 5px;
        }
        .file-meta {
            font-size: 0.9em;
            color: #666;
        }
        .file-actions {
            display: flex;
            gap: 10px;
        }
        .upload-form {
            background: #f0f9ff;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .status-success {
            background: #d1fae5;
            color: #065f46;
        }
        .status-error {
            background: #fee2e2;
            color: #991b1b;
        }
        .status-warning {
            background: #fef3c7;
            color: #92400e;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🪣 S3 Bucket Manager</h1>
        </header>
        
        <main>
            <?php if ($message): ?>
                <div class="success-message"><?php echo $message; ?></div>
            <?php endif; ?>
            
            <?php if ($error): ?>
                <div class="error-message"><?php echo $error; ?></div>
            <?php endif; ?>
            
            <div class="info-section">
                <h3>Bucket Status</h3>
                <ul>
                    <li><strong>Bucket Name:</strong> <?php echo htmlspecialchars($bucketName); ?></li>
                    <li><strong>Region:</strong> <?php echo htmlspecialchars($bucketRegion); ?></li>
                    <li><strong>AWS CLI:</strong> 
                        <?php if ($awsCliAvailable): ?>
                            <span class="status-badge status-success">✅ Available</span>
                        <?php else: ?>
                            <span class="status-badge status-error">❌ Not Available</span>
                        <?php endif; ?>
                    </li>
                    <li><strong>Files in Bucket:</strong> <?php echo count($files); ?></li>
                </ul>
                
                <?php if ($awsCliAvailable): ?>
                <form method="POST" style="margin-top: 10px;">
                    <input type="hidden" name="action" value="test_connection">
                    <button type="submit" class="btn btn-primary">🔍 Test Bucket Connection</button>
                </form>
                <?php endif; ?>
            </div>
            
            <?php if ($awsCliAvailable): ?>
            <!-- Upload Form -->
            <div class="upload-form">
                <h3>📤 Upload File to Bucket</h3>
                <form method="POST" enctype="multipart/form-data">
                    <input type="hidden" name="action" value="upload">
                    <div style="margin: 15px 0;">
                        <input type="file" name="file" required style="padding: 10px;">
                    </div>
                    <button type="submit" class="btn btn-success">Upload to S3</button>
                </form>
                <p style="margin-top: 10px; color: #666; font-size: 0.9em;">
                    Files will be uploaded to: uploads/<?php echo date('Y-m-d'); ?>/
                </p>
            </div>
            
            <!-- File List -->
            <div class="info-section">
                <h3>📁 Files in Bucket</h3>
                
                <?php if (empty($files)): ?>
                    <p><em>No files in bucket yet. Upload your first file above!</em></p>
                <?php else: ?>
                    <div class="file-list">
                        <?php foreach ($files as $file): ?>
                            <div class="file-item">
                                <div class="file-info">
                                    <div class="file-name">📄 <?php echo htmlspecialchars(basename($file['key'])); ?></div>
                                    <div class="file-meta">
                                        Path: <?php echo htmlspecialchars($file['key']); ?><br>
                                        Size: <?php echo formatBytes($file['size']); ?> | 
                                        Date: <?php echo htmlspecialchars($file['date']); ?>
                                    </div>
                                </div>
                                <div class="file-actions">
                                    <a href="bucket-download.php?key=<?php echo urlencode($file['key']); ?>" 
                                       class="btn btn-primary" target="_blank">
                                        ⬇️ Download
                                    </a>
                                    <form method="POST" style="display: inline;" 
                                          onsubmit="return confirm('Delete this file?');">
                                        <input type="hidden" name="action" value="delete">
                                        <input type="hidden" name="file_key" value="<?php echo htmlspecialchars($file['key']); ?>">
                                        <button type="submit" class="btn btn-danger">🗑️ Delete</button>
                                    </form>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </div>
            
            <!-- Quick Actions -->
            <div class="info-section">
                <h3>⚡ Quick Actions</h3>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <a href="bucket-demo.php" class="btn btn-primary">📚 View Documentation</a>
                    <a href="index.php" class="btn btn-primary">🏠 Back to Home</a>
                </div>
            </div>
            
            <?php else: ?>
            <!-- AWS CLI Not Available -->
            <div class="info-section">
                <h3>⚠️ AWS CLI Required</h3>
                <p>The AWS CLI is not installed on this server. To use the bucket manager, install it:</p>
                <pre><code>sudo apt-get update
sudo apt-get install -y awscli</code></pre>
                <p>After installation, refresh this page.</p>
            </div>
            <?php endif; ?>
        </main>
        
        <footer>
            <p>&copy; 2025 S3 Bucket Manager</p>
        </footer>
    </div>
</body>
</html>
