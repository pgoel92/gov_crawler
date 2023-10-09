import boto3
import os

s3 = boto3.client('s3')
files = os.listdir('./uscis/data/txt')
for i, filename in enumerate(files):
    s3.upload_file(Bucket='goelprat', Key=f'kendra/{filename}', Filename='./uscis/data/txt/' + filename)

files = os.listdir('./uscis/data/meta')
for i, filename in enumerate(files):
    s3.upload_file(Bucket='goelprat', Key=f'kendra/{filename}', Filename='./uscis/data/meta/' + filename)
