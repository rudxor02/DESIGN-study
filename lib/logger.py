def setup_logger():
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(process)d:%(name)s:%(lineno)s] [%(levelname)s] %(message)s",
    )
