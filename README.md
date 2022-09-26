# Shift Left Workshop

## Overview
This repo contains the [Shift Left](). Refer to the [Getting Started]() guide for details.

## Repo structure

```bash
├── cdk                               <-- AWS CDK applications for deploying CI/CD pipeline, cfn-guard app, and IDE environment
    └── app                           <-- IaC and cfn-guard rules
    └── cicd                          <-- CICD pipeline to deploy IaC
    └── ide                           <-- Development environment includes bootstrap.sh. it installs all tools needed for this workshop
├── terraform                         <-- Terraform application.
```
