#!/bin/bash
sudo yum update -y
#Add commands here to taste.
# only switch to ec2-user if you are running from ssm run command otherwise cloud9 gives you an interactive shell
#sudo su - ec2-user

#HOME_DIR=$(cd "$(dirname "$0")/.." && pwd)
HOME_DIR="/home/ec2-user"
BIN_DIR="$HOME_DIR/bin"
ENV_DIR="$HOME_DIR/environment"
TMP_DIR="$HOME_DIR/tmp"

#Set environment variables
sudo yum -y install jq bash-completion
echo "export AWS_DEFAULT_REGION=`curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .region`" >>  $HOME_DIR/.bash_profile
echo "export AWS_ACCOUNT_ID=`curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .accountId`" >>  $HOME_DIR/.bash_profile
#.  $HOME_DIR/.bash_profile
#source $HOME_DIR/.bash_profile

# Make directory for tools
mkdir -p $BIN_DIR
mkdir -p $TMP_DIR

#Clone the workshop repo
#cd $ENV_DIR;git clone https://github.com/aws-samples/shiftleft.git

#Install Rust and Cargo
#cd $HOME_DIR
#curl https://sh.rustup.rs -sSf | sh -s -- -y
#source $HOME_DIR/.cargo/env

#Install cfn-guard
# Latest official build - via Cargo
#~/.cargo/bin/cargo install cfn-guard 

#Latest official build - download and install
#$ curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/aws-cloudformation/cloudformation-guard/main/install-guard.sh | sh

# Beta / RC build
#cd $TMP_DIR
# Binary - doesn't currently work on Amazon Linux 2 - fails with gclib version error
#wget https://github.com/aws-cloudformation/cloudformation-guard/releases/download/v2.1.0-pre-rc1/cfn-guard-v2-ubuntu-latest.tar.gz

# Build from source - slower. but works on Amazon Linux 2
#wget https://github.com/aws-cloudformation/cloudformation-guard/archive/refs/tags/v2.1.0-pre-rc1.zip
#unzip v2.1.0-pre-rc1.zip
#cd cloudformation-guard-2.1.0-pre-rc1/
#cd cfn-guard-v2-ubuntu-latest 
#RUSTFLAGS=-Awarnings ~/.cargo/bin/cargo build --release
#cp ./target/release/cfn-guard $BIN_DIR
#cfn-guard --version


# Install Python 3.8
sudo amazon-linux-extras install python3.8 -y

# Uninstall AWSCLI v1
sudo pip2 uninstall awscli -y

# Install AWSCLI v2
cd $TMP_DIR
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && sudo ./aws/install
source $HOME_DIR/.bashrc

# Configure Python virtual environment 
cd $HOME_DIR
python3.8 -m venv $HOME_DIR/.env
source $HOME_DIR/.env/bin/activate

# Install CDK python modules
cd $HOME_DIR
pip install -r $HOME_DIR/environment/shiftleft/cdk/app/requirements.txt
pip install -r $HOME_DIR/environment/shiftleft/cdk/cicd/requirements.txt


# Change directory to shiftleft
cd $HOME_DIR/environment/shiftleft

# Install NodeJS and NPM
#wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
#source $HOME_DIR/.bashrc
#source $HOME_DIR/.bash_profile

# Install CDK v1
npm install -g aws-cdk@1.174.0 --force
#cdk --version
#source $HOME_DIR/.bashrc
#source $HOME_DIR/.bash_profile

# Deploy the pipeline for student exercises
#cd $HOME_DIR/environment/shiftleft/cdk/cicd
#pip install -r requirements.txt
#cdk bootstrap
#cdk deploy --all --require-approval never
