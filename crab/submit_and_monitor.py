#!/usr/bin/env python3
"""Submit and monitor NanoAODTools CRAB jobs.

This helper wraps the CRAB API to submit post-processing tasks and
periodically report the status of every job.  A short log is written to
``crab_status.log`` and the information is also printed on the terminal.

Example
-------

Submit two datasets and check progress every 10 minutes::

    python submit_and_monitor.py --datasets /A/B/C /D/E/F --interval 600

"""

import argparse
import copy
import logging
import time

from CRABAPI.RawCommand import crabCommand

# Reuse the base configuration shipped with NanoAODTools.  The script will
# clone it for each dataset and only update the request name and input
# dataset.
from crab_cfg import config as base_config


def submit_task(dataset, request_name):
    """Submit a CRAB task for *dataset* and return its task directory."""
    cfg = copy.deepcopy(base_config)
    cfg.General.requestName = request_name
    cfg.Data.inputDataset = dataset
    crabCommand("submit", config=cfg)
    # CRAB creates a directory named ``crab_<requestName>`` for each task
    return f"crab_{request_name}"


def monitor_task(task_dir, interval):
    """Poll *task_dir* every *interval* seconds and log job statuses."""
    while True:
        status = crabCommand("status", dir=task_dir)
        summary = status.get("jobsPerStatus", {})
        total = sum(summary.values())
        finished = summary.get("finished", 0)
        logging.info("Task %s: %d/%d jobs finished", task_dir, finished, total)

        # Log the state of each individual job so unfinished jobs can be
        # quickly identified.
        for job in status.get("jobList", []):
            logging.info("  Job %s: %s", job.get("jobid"), job.get("state"))

        if finished >= total:
            logging.info("Task %s: all jobs finished", task_dir)
            break
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(
        description="Submit and monitor NanoAODTools CRAB jobs")
    parser.add_argument(
        "--datasets",
        nargs="+",
        required=True,
        help="List of input datasets",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=600,
        help="Polling interval in seconds (default: 600)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("crab_status.log", mode="w"),
        ],
    )

    for dataset in args.datasets:
        # Build a human readable request name.  Keep it short to satisfy CRAB
        # limits on the request name length.
        request = dataset.strip("/").replace("/", "_")[:100]
        logging.info("Submitting dataset %s", dataset)
        task_dir = submit_task(dataset, request)
        logging.info("Submitted as %s", task_dir)
        monitor_task(task_dir, args.interval)


if __name__ == "__main__":
    main()

