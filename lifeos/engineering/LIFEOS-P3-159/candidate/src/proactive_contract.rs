//! Closed provider-neutral candidates. References never grant authority.
use crate::repository::Error;
use serde::{Deserialize, Serialize};
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Span {
    pub message_ref: String,
    pub start: usize,
    pub end: usize,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum Evaluation {
    Silence {
        #[serde(rename = "reasonCode")]
        reason_code: SilenceReason,
    },
    Question {
        #[serde(rename = "subjectRefs")]
        subject_refs: Vec<String>,
        question: String,
        #[serde(rename = "whyNow")]
        why_now: String,
        #[serde(rename = "evidenceRefs")]
        evidence_refs: Vec<String>,
        #[serde(rename = "inferenceFlags")]
        inference_flags: Vec<String>,
    },
    Suggestion {
        #[serde(rename = "subjectRefs")]
        subject_refs: Vec<String>,
        proposal: String,
        #[serde(rename = "whyNow")]
        why_now: String,
        #[serde(rename = "evidenceRefs")]
        evidence_refs: Vec<String>,
        #[serde(rename = "inferenceFlags")]
        inference_flags: Vec<String>,
    },
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum SilenceReason {
    NoUsefulIntervention,
    ContextInsufficient,
    AlreadyReasonablyPlanned,
    UnclearSubject,
    Suppressed,
    NoNewValue,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum FeedbackIntent {
    ContextUpdate {
        #[serde(rename = "subjectRefs")]
        subject_refs: Vec<String>,
        #[serde(rename = "userEvidenceSpans")]
        spans: Vec<Span>,
        value: String,
        #[serde(rename = "validUntil")]
        valid_until: i64,
    },
    Snooze {
        #[serde(rename = "subjectRefs")]
        subject_refs: Vec<String>,
        #[serde(rename = "userEvidenceSpans")]
        spans: Vec<Span>,
        #[serde(rename = "timeText")]
        time_text: String,
        #[serde(rename = "intervalStart")]
        interval_start: i64,
        #[serde(rename = "intervalEnd")]
        interval_end: i64,
        timezone: String,
    },
    Suppress {
        #[serde(rename = "subjectRefs")]
        subject_refs: Vec<String>,
        #[serde(rename = "userEvidenceSpans")]
        spans: Vec<Span>,
        enabled: bool,
    },
    Correct {
        #[serde(rename = "subjectRefs")]
        subject_refs: Vec<String>,
        #[serde(rename = "userEvidenceSpans")]
        spans: Vec<Span>,
        #[serde(rename = "replacementFact")]
        replacement_fact: Option<String>,
    },
    Clarify {
        #[serde(rename = "subjectRefs")]
        subject_refs: Vec<String>,
        #[serde(rename = "userEvidenceSpans")]
        spans: Vec<Span>,
        question: String,
    },
    Discuss {
        #[serde(rename = "subjectRefs")]
        subject_refs: Vec<String>,
        #[serde(rename = "userEvidenceSpans")]
        spans: Vec<Span>,
        answer: String,
        #[serde(rename = "relatedToSuggestion")]
        related: bool,
    },
    ActionIntent {
        #[serde(rename = "subjectRefs")]
        subject_refs: Vec<String>,
        #[serde(rename = "userEvidenceSpans")]
        spans: Vec<Span>,
        candidate: serde_json::Value,
    },
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Response {
    pub feedback: Vec<FeedbackIntent>,
}
pub fn reject() -> Error {
    Error::new("proactive_candidate_rejected")
}
pub fn bounded(s: &str, max: usize) -> Result<(), Error> {
    if s.trim().is_empty() || s.chars().count() > max || s.contains('\0') {
        Err(reject())
    } else {
        Ok(())
    }
}
pub fn refs(xs: &[String], allowed: &[String], max: usize) -> Result<(), Error> {
    if xs.is_empty()
        || xs.len() > max
        || xs
            .iter()
            .enumerate()
            .any(|(i, x)| !allowed.contains(x) || xs[..i].contains(x))
    {
        Err(reject())
    } else {
        Ok(())
    }
}
pub fn spans(xs: &[Span], current: &str) -> Result<(), Error> {
    let n = current.chars().count();
    if xs.is_empty()
        || xs.len() > 4
        || xs
            .iter()
            .any(|s| s.message_ref != "current" || s.start >= s.end || s.end > n)
    {
        Err(reject())
    } else {
        Ok(())
    }
}
impl Evaluation {
    pub fn validate(&self, subjects: &[String], evidence: &[String]) -> Result<(), Error> {
        match self {
            Self::Silence { .. } => Ok(()),
            Self::Question {
                subject_refs,
                question,
                why_now,
                evidence_refs,
                inference_flags,
            } => {
                bounded(question, 1600)?;
                Self::common(
                    subject_refs,
                    why_now,
                    evidence_refs,
                    inference_flags,
                    subjects,
                    evidence,
                )
            }
            Self::Suggestion {
                subject_refs,
                proposal,
                why_now,
                evidence_refs,
                inference_flags,
            } => {
                bounded(proposal, 1600)?;
                Self::common(
                    subject_refs,
                    why_now,
                    evidence_refs,
                    inference_flags,
                    subjects,
                    evidence,
                )
            }
        }
    }
    fn common(
        s: &[String],
        why: &str,
        e: &[String],
        f: &[String],
        subjects: &[String],
        evidence: &[String],
    ) -> Result<(), Error> {
        refs(s, subjects, 8)?;
        refs(e, evidence, 8)?;
        bounded(why, 600)?;
        if f.len() > 4
            || f.iter()
                .any(|x| !["inference", "unknown_progress", "prediction"].contains(&x.as_str()))
        {
            return Err(reject());
        }
        Ok(())
    }
}
impl FeedbackIntent {
    pub fn subjects(&self) -> &Vec<String> {
        match self {
            Self::ContextUpdate { subject_refs, .. }
            | Self::Snooze { subject_refs, .. }
            | Self::Suppress { subject_refs, .. }
            | Self::Correct { subject_refs, .. }
            | Self::Clarify { subject_refs, .. }
            | Self::Discuss { subject_refs, .. }
            | Self::ActionIntent { subject_refs, .. } => subject_refs,
        }
    }
    pub fn evidence(&self) -> &Vec<Span> {
        match self {
            Self::ContextUpdate { spans, .. }
            | Self::Snooze { spans, .. }
            | Self::Suppress { spans, .. }
            | Self::Correct { spans, .. }
            | Self::Clarify { spans, .. }
            | Self::Discuss { spans, .. }
            | Self::ActionIntent { spans, .. } => spans,
        }
    }
}
impl Response {
    pub fn validate(
        &self,
        subjects: &[String],
        current: &str,
        at: i64,
        day_end: i64,
        tz: &str,
    ) -> Result<(), Error> {
        if self.feedback.is_empty() || self.feedback.len() > 2 {
            return Err(reject());
        }
        for f in &self.feedback {
            refs(f.subjects(), subjects, 8)?;
            spans(f.evidence(), current)?;
            match f {
                FeedbackIntent::ContextUpdate {
                    value, valid_until, ..
                } => {
                    bounded(value, 600)?;
                    if *valid_until <= at || *valid_until > day_end {
                        return Err(reject());
                    }
                }
                FeedbackIntent::Snooze {
                    time_text,
                    interval_start,
                    interval_end,
                    timezone,
                    ..
                } => {
                    bounded(time_text, 200)?;
                    if !current.contains(time_text.as_str())
                        || timezone != tz
                        || *interval_start <= at
                        || interval_end < interval_start
                    {
                        return Err(reject());
                    }
                }
                FeedbackIntent::ActionIntent { candidate, .. } => {
                    let o = candidate.as_object().ok_or_else(reject)?;
                    let op = candidate["operation"].as_str().ok_or_else(reject)?;
                    let content = ["create", "adjust"].contains(&op);
                    if !["create", "adjust", "complete", "cancel"].contains(&op)
                        || o.len() != if content { 2 } else { 1 }
                        || o.keys().any(|k| k != "operation" && k != "content")
                    {
                        return Err(reject());
                    }
                    if content {
                        bounded(candidate["content"].as_str().ok_or_else(reject)?, 500)?
                    }
                }
                FeedbackIntent::Correct {
                    replacement_fact: Some(v),
                    ..
                } => bounded(v, 600)?,
                FeedbackIntent::Clarify { question, .. } => bounded(question, 200)?,
                FeedbackIntent::Discuss { answer, .. } => bounded(answer, 1600)?,
                _ => (),
            }
        }
        if self.feedback.len() == 2 {
            let a = &self.feedback[0];
            let b = &self.feedback[1];
            if a.subjects() != b.subjects() {
                return Err(reject());
            }
            let action = matches!(a, FeedbackIntent::ActionIntent { .. }) as u8
                + matches!(b, FeedbackIntent::ActionIntent { .. }) as u8;
            let has_context=self.feedback.iter().any(|f|matches!(f,FeedbackIntent::ContextUpdate{..}));
            let has_snooze=self.feedback.iter().any(|f|matches!(f,FeedbackIntent::Snooze{..}));
            let has_discussion=self.feedback.iter().any(|f|matches!(f,FeedbackIntent::Discuss{related:true,..}));
            let has_suppress=self.feedback.iter().any(|f|matches!(f,FeedbackIntent::Suppress{..}));
            let compatible=action==1&&(has_context||has_snooze)||action==0&&has_context&&(has_snooze||has_suppress||has_discussion);
            if !compatible {
                return Err(reject());
            }
        }
        Ok(())
    }
}
