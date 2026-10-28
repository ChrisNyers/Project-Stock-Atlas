"""Stock Atlas decision UI — integration layer over the EXISTING frozen engine.

This package is presentation + thin server-side adapters. It computes no Stage 7
eligibility, creates no PortfolioAction, ranks nothing, and writes capital records
only through ``CapitalDecisionFacade``. Paper decisions only; no real trades.
"""
