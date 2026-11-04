---
layout: concepts
permalink: /en/terms/
lang: en
title: "Concept dictionary — Meep Examples"
lesson_title: "Meep concept dictionary"
lesson_summary: "FDTD concepts you need when writing Meep code and reading its results, one entry at a time. Every entry follows the same order: definition and equations, the Meep code block, how the examples use it, cases where the code runs but the result is wrong, and what changes in inverse design."
axes:
  - { key: numerics, label: "Numerics", note: "Concepts that come from FDTD as a computational method: grid and time step, boundaries, convergence." }
  - { key: block, label: "Meep building blocks", note: "Pieces you use as a unit in Meep code, such as sources, monitors, boundaries and materials, and the rules for using them." }
  - { key: validation, label: "Validation", note: "Ways to check that a run that finished actually gave the right answer, such as convergence checks and energy conservation." }
  - { key: em, label: "Electromagnetics", note: "Physical concepts needed to interpret results, such as polarization, modes, diffraction and LDOS." }
  - { key: invdes, label: "Inverse design", note: "Concepts that appear in inverse design: design regions, objectives, adjoint gradients." }
---

The [official Meep documentation](https://meep.readthedocs.io/en/master/) explains the API and tutorials well, but which line of code a concept corresponds to, and which mistakes quietly make a result wrong, is spread across many pages. This dictionary gathers that by concept. Numbers are quoted from this site's example lessons or from Meep runs made for the entry, and sentences taken from the official docs are linked.

Every entry has the same seven sections: what it is · why it matters · in Meep code · in the examples · runs, but wrong · in inverse design · connections. If a concept in a lesson is new to you, read sections 1 and 3 first; if a result looks odd, start from the symptom table in section 5.

Entries are added in the order the concepts appear in the example lessons.
