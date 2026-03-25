"""MES data models — all shared dataclasses."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RoBAssessment:
    """Risk of Bias assessment for a single study."""
    tool: str  # "RoB2" or "ROBINS-I"
    overall: str  # "low", "some_concerns", "high"
    domains: dict[str, str] = field(default_factory=dict)


@dataclass
class StudyDossier:
    """Annotated study — output of ASSESS phase."""
    study_id: str
    yi: float
    vi: float
    measure: str  # "logOR", "logRR", "SMD", etc.
    design_type: str = "RCT"
    design_tier: int = 1  # 1=RCT, 2=quasi/MR, 3=observational
    rob: Optional[RoBAssessment] = None
    year: Optional[int] = None
    n1: Optional[int] = None
    n2: Optional[int] = None
    events1: Optional[int] = None
    events2: Optional[int] = None


@dataclass
class BiasProfile:
    """Review-level bias detection results (from ASSESS)."""
    egger_p: Optional[float] = None
    begg_p: Optional[float] = None
    excess_sig_count: int = 0
    k: int = 0


@dataclass
class MESSpec:
    """Declarative specification for the multiverse analysis."""
    estimators: list[str] = field(
        default_factory=lambda: ["FE", "DL", "REML", "PM", "SJ", "ML"]
    )
    ci_methods: list[str] = field(
        default_factory=lambda: ["Wald", "HKSJ", "t-dist"]
    )
    bias_corrections: list[str] = field(
        default_factory=lambda: ["none", "trim-fill", "PET-PEESE", "selection-model"]
    )
    quality_filters: list[str] = field(
        default_factory=lambda: ["all", "exclude-high-rob", "low-rob-only"]
    )
    design_filters: list[str] = field(
        default_factory=lambda: ["all", "rct-quasi", "rct-only"]
    )
    sensitivity: list[str] = field(
        default_factory=lambda: ["full", "loo"]
    )
    alpha: float = 0.05

    @property
    def base_spec_count(self) -> int:
        return (
            len(self.estimators)
            * len(self.ci_methods)
            * len(self.bias_corrections)
            * len(self.quality_filters)
            * len(self.design_filters)
        )


@dataclass
class SpecResult:
    """Result from a single specification execution."""
    spec_id: str
    estimator: str
    ci_method: str
    bias_correction: str
    quality_filter: str
    design_filter: str
    sensitivity: str
    theta: float
    se: float
    ci_lo: float
    ci_hi: float
    p_value: float
    tau2: float
    I2: float
    k: int
    pi_lo: float
    pi_hi: float
    significant: bool
    direction: str
    converged: bool = True
    error: Optional[str] = None


@dataclass
class ConcordanceMetrics:
    """Concordance analysis results."""
    C_dir: float
    C_sig: float
    C_full: float
    n_specs: int
    n_feasible: int


@dataclass
class MESVerdict:
    """Final MES evidence landscape verdict."""
    overall_class: str
    overall_c_sig: float
    conditional: dict
    dominant_dimension: str
    dominant_eta2: float
    certification: str
    eta2_all: dict[str, float] = field(default_factory=dict)
    boundaries: dict = field(default_factory=dict)
    prediction_null_rate: float = 0.0
