import matplotlib
import matplotlib.pyplot as plot


__backend = None
__parameters = None

pgf_parameters = {
    "pgf.texsystem": "pdflatex",
    "text.usetex": True,
    "figure.figsize": (3.1, 2.5),
    "pgf.preamble": [
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[T1]{fontenc}",
        r"\renewcommand{\familydefault}{\sfdefault}"
    ],
    "font.family": "serif",
    "font.size": 10,
    "font.serif": [],  # Defaults to Computer Modern
    "font.sans-serif": [],
    "font.monospace": [],
    "axes.labelsize": 10,
    "legend.fontsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "axes.linewidth": 0.5,
    "grid.linewidth": 0.5,
    "lines.linewidth": 0.5
}


def init(parameters=None):
    global __backend
    global __parameters

    __backend = plot.get_backend()
    __parameters = matplotlib.rcParams.copy()

    plot.switch_backend("pgf")
    matplotlib.rcParams.update(pgf_parameters)
    if parameters is not None:
        matplotlib.rcParams.update(parameters)


def publish(prefix, extension):
    plot.tight_layout(pad=0.5)
    plot.savefig(
        prefix + "." + extension,
        dpi=400 if extension == "pdf" else 200)
