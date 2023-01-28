#!/usr/bin/env python
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    from firefly_iii_automation import wave_app
