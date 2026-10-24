---
layout: rights
title: "Rights & Licenses"
description: "Upstream sources, contributions added by this project, and conditions for using the code, articles and illustrations."
permalink: /en/rights-and-licenses/
lang: en
updated: "2026-10-24"
toc:
  - { id: scope, label: "Maintainer and rights" }
  - { id: reuse, label: "Reusing material" }
  - { id: code, label: "Code and restructuring" }
  - { id: images, label: "Figures and AI tools" }
  - { id: sources, label: "Sources and additions" }
  - { id: third-party, label: "Software and contact" }
---

<h2 id="scope">Maintainer and rights</h2>

This Meep learning project is maintained and edited by [jin-castle](https://github.com/jin-castle). It is not an official Meep website or part of its official documentation, and does not imply endorsement or affiliation with upstream developers or paper authors.

Project additions include Korean/English explanations and learning sequences, the observe–predict–run–interpret structure, additional experiments and validation, shared figure helpers, execution records, and website design and interactions. This describes work added to the project; it does not claim that every element was independently authored by one person or qualifies for exclusive copyright. AI tools have assisted code, translation and illustration workflows.

Upstream examples, libraries, papers and quoted material remain subject to their respective rights. No exclusive rights are claimed over physical laws, general ideas or algorithms, or bare numerical facts. Any future collaborative, institutional or sponsored research must identify its own agreements and contributions.

<h2 id="reuse">Reusing material</h2>

- **Upstream and third-party material:** Its own license and copyright notices take precedence. This page does not restrict permissions already granted by those licenses.
- **New project articles, creative diagrams and presentation:** Rights in protectable creative expression are reserved unless otherwise stated. Attribution alone does not grant permission to reproduce, translate or redistribute an entire article. Statutory exceptions, including permitted quotation, remain applicable.
- **Code:** No new repository-wide MIT or Creative Commons license is granted. Check upstream licenses and file-specific terms first. For permission concerning independently authored additions, identify the files in your request.
- **Computed figures and AI illustrations:** Check the production methods and exceptions below. Public availability or a generation record does not by itself establish exclusive ownership or permission for reuse.

When introducing a lesson, please identify the maintainer, article title, page URL and access date. Example: `jin-castle, “Cylindrical coordinates and rotational symmetry,” Meep Examples, page URL, access date`.

<h2 id="code">Code and restructuring</h2>

Splitting programs into functions, classes and configuration files, adding shared helpers, and separating experiments from verification can improve learning and reproducibility. However, **reorganizing, modifying or renaming upstream code does not remove its license obligations.** Applicable upstream terms, copyright notices, required source and modification notices must be preserved when modifying or distributing it.

The [official Meep license clarification](https://meep.readthedocs.io/en/latest/License_and_Copyright/) identifies Meep as GNU GPL version 2 or later. It explains that user-written Python/Scheme control files loaded at runtime **which do not contain code distributed with Meep** do not thereby fall under those GPL restrictions. Copied or adapted examples and independently written control files must be distinguished.

Several scientific scripts and lessons in this repository explicitly identify official examples and changed conditions. This inventory records references and added work; it is not a completed line-by-line audit establishing copied versus independently written statements in every file. Upstream-derived material is not claimed as exclusive project code or relicensed merely because it was restructured. See [THIRD_PARTY_NOTICES.md](https://github.com/jin-castle/meep-examples/blob/main/THIRD_PARTY_NOTICES.md) for the Meep notice and GPL-copy location.

<h2 id="images">Figures and AI tools</h2>

**Concept illustrations:** The 14 chapter illustrations in `assets/illustrations/` are explanatory PNGs made with imagegen. Each chapter has Korean/English and light/dark variants. Prompts, dimensions and hashes are recorded in the [generation manifest]({{ '/assets/illustrations/manifest.json' | relative_url }}). These illustrations are not computed fields or optimization results.

**Computed figures:** Fields, spectra, densities and GIFs in `assets/meep/` are associated with published execution/rendering code and calculation records. They are not generatively repainted or color-inverted for a theme. Producing a new rendering does not transfer rights in upstream code, models or referenced material.

**Reused-image exception:** The left panel of Optical beams' `gallery/vortex_3d_comparison.png` reuses an original image from Daniel Kotik's project. The [pinned upstream image](https://github.com/DanielKotik/Optical-beams-MEEP/blob/ca145119e5bd0f0804d846ea42e35e4c3daa91de/scripts/Laguerre_Gauss_3d/img/vortex_beam_m_2_3d_half_resized.png) and [comparison provenance]({{ '/assets/meep/optical-beams/gallery/comparison-provenance.json' | relative_url }}) are retained.

No automatic exclusive human copyright is claimed over entire AI outputs. Human-authored, creatively edited or arranged contributions must be distinguished from generated material; protection depends on the actual contribution. The manifest records production, rather than copyright registration or exclusive ownership. See the [Korea Copyright Commission guide](https://library.copyright.or.kr/userInfo.do/10220/contents/7522251).

<h2 id="sources">Sources and project additions</h2>

The following inventory covers the main sources, implementations and additions for all 14 lessons and two topic guides. Each lesson's references provide further APIs, papers and relevant issues. Meep `latest` documentation and `master` code links can change and do not pin the exact source of a past execution. Published main runs identify Meep 1.33.0; the Optical-beams upstream source is separately commit-pinned.

{% include source-inventory.html %}

<h2 id="third-party">Software and contact</h2>

- **Meep:** Massachusetts Institute of Technology and contributors; GPL version 2 or later. The Python control-file clarification has the scope described above.
- **Optical-beams-MEEP:** A project by Daniel Kotik and Jörg Götte. Preserved upstream code uses the MIT License; its `Copyright (c) 2018 Daniel Kotik` notice and [full license](https://github.com/jin-castle/meep-examples/blob/main/code/optical_beams/source/LICENSE) are retained.
- **GSAP 3.15.0:** GreenSock, [GSAP Standard License](https://gsap.com/standard-license/). The vendored browser distribution retains the upstream notice.
- **MathJax 2.7.9:** Formula rendering loaded from cdnjs, [Apache License 2.0](https://github.com/mathjax/MathJax/blob/2.7.9/LICENSE).
- **Jekyll, Minima and build tools:** Used through GitHub Pages. Version-specific licenses and links are recorded in the notices. Font family names in CSS are installed-font fallbacks; font files are not distributed here.

Read [THIRD_PARTY_NOTICES.md](https://github.com/jin-castle/meep-examples/blob/main/THIRD_PARTY_NOTICES.md) for scope, versions, original notices and known limitations. For attribution corrections or permission requests, contact the maintainer through the [GitHub repository](https://github.com/jin-castle/meep-examples), identifying the page/file and intended use.
