const AWS = require('aws-sdk');
const multer = require('multer');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

// Configure AWS
AWS.config.update({
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    region: process.env.AWS_REGION || 'us-east-1'
});

const s3 = new AWS.S3();

// Multer configuration for memory storage
const storage = multer.memoryStorage();

const fileFilter = (req, file, cb) => {
    // Accept only image files
    if (file.mimetype.startsWith('image/')) {
        cb(null, true);
    } else {
        cb(new Error('Only image files are allowed!'), false);
    }
};

const upload = multer({
    storage: storage,
    fileFilter: fileFilter,
    limits: {
        fileSize: 5 * 1024 * 1024 // 5MB limit
    }
});

// Function to upload file to S3
const uploadToS3 = async (file, folder = 'uploads') => {
    const fileExtension = file.originalname.split('.').pop();
    const fileName = `${folder}/${uuidv4()}.${fileExtension}`;
    
    const params = {
        Bucket: process.env.S3_BUCKET_NAME,
        Key: fileName,
        Body: file.buffer,
        ContentType: file.mimetype,
        ACL: 'public-read'
    };

    try {
        const result = await s3.upload(params).promise();
        return result.Location;
    } catch (error) {
        throw new Error(`S3 upload failed: ${error.message}`);
    }
};

// Function to delete file from S3
const deleteFromS3 = async (fileUrl) => {
    try {
        const key = fileUrl.split('/').slice(-2).join('/'); // Extract key from URL
        const params = {
            Bucket: process.env.S3_BUCKET_NAME,
            Key: key
        };
        
        await s3.deleteObject(params).promise();
        return true;
    } catch (error) {
        throw new Error(`S3 delete failed: ${error.message}`);
    }
};

module.exports = {
    upload,
    uploadToS3,
    deleteFromS3,
    s3
};
