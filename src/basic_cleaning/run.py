#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)
    logger.info("Running basic_cleaning job...")

    # Download input artifact
    local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(local_path)
    logger.info("Downloaded the input artifact: {}".format(args.input_artifact))
    
    # Drop outliers
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()
    logger.info("Drop outliers between the price of {} and {}".format(min_price, max_price))
    
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])
    
    # Drop rows in the dataset that are not in the proper geolocation
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    df.to_csv("./output/clean_sample.csv", index=False)
    logger.info("Save the new artifact as clean_sample.csv")
    
    # Upload clean file
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description
    )
    artifact.add_file("./output/clean_sample.csv")
    run.log_artifact(artifact)
    artifact.wait()
    logger.info("Upload clean_sample.csv to W&B")    
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Path to the input artifact",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Path to the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type of the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Output description",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price",
        required=True
    )


    args = parser.parse_args()

    go(args)
