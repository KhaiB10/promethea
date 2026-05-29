# Promethea reproducible dev environment.
#
# Provides: OpenMC (with depletion + cross-section data), Python 3.11,
# scientific stack, and the Promethea source tree.
#
# Build:   docker build -t promethea:dev .
# Run:     docker run --rm -it -v $PWD:/workspace promethea:dev bash
# Smoke:   docker run --rm -v $PWD:/workspace promethea:dev \
#              python /workspace/scripts/hello_reactor.py

FROM mambaorg/micromamba:1.5.10

LABEL org.opencontainers.image.title="Promethea"
LABEL org.opencontainers.image.description="Open-source continual-learning autonomous control for advanced MSRs"
LABEL org.opencontainers.image.source="https://github.com/KhaiB10/promethea"
LABEL org.opencontainers.image.licenses="MIT"

# Install everything from conda-forge in one resolution pass.
# OpenMC ships there with MPI + HDF5 + the depletion module wired up.
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential \
    && rm -rf /var/lib/apt/lists/*
USER $MAMBA_USER

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
RUN micromamba install -y -n base -f /tmp/environment.yml && \
    micromamba clean --all --yes

# Activate the env for every subsequent command.
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# Cross-section library. ENDF/B-VIII.0 is the modern default; ~4 GB.
# Skipped at build time to keep the image small — fetched on first run
# by scripts/fetch_xs.sh into /workspace/data/xs/.
ENV OPENMC_CROSS_SECTIONS=/workspace/data/xs/endfb-viii.0-hdf5/cross_sections.xml

WORKDIR /workspace
CMD ["bash"]
