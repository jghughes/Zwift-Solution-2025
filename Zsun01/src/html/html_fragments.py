FOOTNOTES = """
<div class="footnote">
    <div class="footnote-item"><sup>1</sup> Pull: Watts and duration for each rider's main pull. Higher ranking riders are prioritised for longer pulls and are located top and bottom of the paceline list, protecting weaker riders in the middle. Standard pulls range between 30 seconds and five minutes and corresponding pull capabilities are taken from a curve fitted to a rider's ZwiftPower data in their 3.5 - 20 minute window. Riders are not ranked according to zFTP, they are ranked according to how hard they can pull for one-minute.</div>
    <div class="footnote-item"><sup>2</sup> zFTP: Zwift Functional Threshold Power. zFTP metrics are displayed, but play no role in computations.</div>
    <div class="footnote-item"><sup>3</sup> NP: Normalized Power. Calculated from rolling-average watts using a five-second window.</div>
    <div class="footnote-item"><sup>4</sup> IF: Intensity factor. Intensity of effort measured in terms of normalised power divided by one-hour pulling capability. One-hour capability is taken from a curve fitted to a rider's ZwiftPower data in the 8 - 40-minute window and extrapolated to one hour. Sigma is the standard deviation of all IFs for the team. Smaller is superior.</div>
    <div class="footnote-item"><sup>5</sup> Limit: For ride plans where everybody pulls, the speed of the paceline is restricted to the available pulling capability of the weakest rider and the intensity of effort of the hardest-working rider. There is no protection for weaker or harder-working riders in other plans.</div>
</div>
"""

PACELINE_PLAN_SUMMARY_CSS_STYLE_SHEET = """
    <style>
        /* =========================================================================
           1. CSS Reset/Normalize
           -------------------------------------------------------------------------
           Removes default browser styling and ensures consistent box-sizing.
           ========================================================================= */
        html, body, div, span, applet, object, iframe,
        h1, h2, h3, h4, h5, h6, p, blockquote, pre,
        a, abbr, acronym, address, big, cite, code,
        del, dfn, em, img, ins, kbd, q, s, samp,
        small, strike, strong, sub, sup, tt, var,
        b, u, i, center,
        dl, dt, dd, ol, ul, li,
        fieldset, form, label, legend,
        table, caption, tbody, tfoot, thead, tr, th, td,
        article, aside, canvas, details, embed,
        figure, figcaption, footer, header, hgroup,
        menu, nav, output, ruby, section, summary,
        time, mark, audio, video {
            margin: 0;
            padding: 0;
            border: 0;
            font-size: 100%;
            font: inherit;
            vertical-align: baseline;
            box-sizing: border-box;
        }

        /* Ensures all elements and pseudo-elements use border-box sizing */
        *, *::before, *::after {
            box-sizing: inherit;
        }

        /* =========================================================================
           2. Base HTML Elements
           -------------------------------------------------------------------------
           Sets up base font, background, and color for the page and headings.
           ========================================================================= */
        body {
            font-family: 'Roboto Mono', 'Consolas', 'Menlo', 'Monaco', monospace;
            background: #fff;
            color: #222;
            margin: 0;
            padding: 1rem 2rem;
        }

        h1 {
            font-family: 'Roboto', Arial, sans-serif;
            font-size: 1.05em;
            font-weight: 700;
            color: #222;
            letter-spacing: 0.01em;
            margin: 0 0 1em 0;
        }

        /* =========================================================================
           3. Layout Containers
           -------------------------------------------------------------------------
           Styles for main containers and section separators.
           ========================================================================= */
        .table-container {
            width: 100%;
            max-width: 100vw;
            margin: 0 auto;
            overflow-x: auto; /* Enables horizontal scrolling for wide tables */
            padding: 0;
        }

        .section-separator {
            margin: 32px 0;
        }
        .section-separator:last-of-type {
            margin-bottom: 0.25em;
        }

        /* =========================================================================
           4. Component Classes - Table Styling
           -------------------------------------------------------------------------
           Styles for the main rider table and its elements.
           ========================================================================= */
        .rider-table {
            border-collapse: collapse;
            width: 100%;
            table-layout: auto;
            font-family: 'Roboto Mono', 'Consolas', 'Menlo', 'Monaco', monospace;
            font-size: 0.95em;
            border: 1px solid #b0b0b0;
        }

        .rider-table caption {
            /* Table caption styled as a heading above the table */
            caption-side: top;
            font-family: 'Roboto', Arial, sans-serif;
            font-size: 1.05em;
            font-weight: 700;
            color: #222;
            letter-spacing: 0.01em;
            text-align: left;
            margin-bottom: 0.50em;
        }

        .rider-table th,
        .rider-table td {
            font-size: 0.95em;
            padding: 6px 6px;
            white-space: nowrap;
            border: 1px solid #b0b0b0;
        }

        .rider-table th {
            background-color: #e6ecf5;
            font-weight: bold;
            text-align: center;
            border-bottom: 2px solid #444;
            letter-spacing: 0.02em;
        }

        .rider-table th.left-header,
        .rider-table td.left-header {
            text-align: left;
        }

        .rider-table th:nth-child(1),
        .rider-table td:nth-child(1),
        .rider-table th:nth-child(2),
        .rider-table td:nth-child(2) {
            /* Use proportional font for first two columns for readability */
            font-family: 'Roboto', Arial, sans-serif;
            font-weight: 400;
        }

        .rider-table tr:nth-child(even) td {
            background-color: #f7fafd; /* Zebra striping for rows */
        }

        .rider-table tr:hover td {
            background-color: #dbeafe; /* Highlight row on hover */
        }

        .rider-table td:nth-child(3),
        .rider-table td:nth-child(9) {
            /* Emphasize key numeric columns with right alignment and background */
            text-align: right;
            font-weight: bold;
            background-color: #f0f4fa;
        }

        .rider-table td:nth-child(4) {
            text-align: left;
        }

        .rider-table td:nth-child(n+5):nth-child(-n+8) {
            /* Right-align columns 5-8 (numeric data) */
            text-align: right;
        }

        /* =========================================================================
           5. Utility and Helper Classes
           -------------------------------------------------------------------------
           Styles for footnotes, summary footnotes, and superscripts.
           ========================================================================= */
        .footnote {
            font-family: 'Roboto', Arial, sans-serif;
            font-size: 0.95em;
            font-weight: 500;
            color: #666;
            text-align: left;
            margin-top: 1.5em;
        }

        .footnote-item {
            margin-bottom: 0.5em;
            padding-left: 2em;
            text-indent: -2em; /* Hanging indent for footnote numbers */
        }

        .footnote-item:hover {
            background-color: #dbeafe;
            transition: background 0.2s;
            cursor: pointer;
        }

        .footnote sup,
        .rider-table th sup {
            font-size: 0.8em;
            vertical-align: super;
            font-weight: bold;
        }

        .summary-footnote {
            margin-top: 0.25em;
            font-size: 0.9em; /* Base size, overridden in media queries */
            color: #666;
        }

        /* =========================================================================
           6. Media Queries
           -------------------------------------------------------------------------
           Responsive and print-specific styles for better usability on small screens
           and for printing. These are more sophisticated and ensure the table is
           readable on mobile and print-friendly.
           ========================================================================= */

        /* --- Extra small devices (max-width: 480px) --- */
        @media (max-width: 480px) {
            body {
                padding: 0.1rem 0.1rem;
            }
            .table-container {
                padding: 0;
            }
            .section-separator {
                margin: 8px 0;
            }
            h1 {
                font-size: 0.85em;
            }
            .rider-table {
                font-size: 0.75em;
            }
            .rider-table caption {
                font-size: 0.75em;
                margin-bottom: 0.15em;
            }
            .rider-table th,
            .rider-table td {
                font-size: 0.7em;
                padding: 2px 1px;
            }
            .footnote,
            .footnote-item {
                font-size: 0.7em;
            }
            .summary-footnote {
                font-size: 0.7em;
            }
        }

        /* --- Small devices (max-width: 600px) --- */        
        @media (max-width: 600px) {
            body {
                padding: 0.25rem 0.25rem;
            }
            .table-container {
                padding: 0;
            }
            .section-separator {
                margin: 16px 0;
            }
            h1 {
                font-size: 0.95em;
            }
            .rider-table {
                font-size: 0.85em;
            }
            .rider-table caption {
                font-size: 0.85em;
                margin-bottom: 0.2em;
            }
            .rider-table th,
            .rider-table td {
                font-size: 0.8em;
                padding: 3px 2px;
            }
            .footnote,
            .footnote-item {
                font-size: 0.8em;
            }
            .summary-footnote {
                font-size: 0.8em;
            }
        }

        /* --- Tablets (max-width: 900px) --- */
        @media (max-width: 900px) {
            body {
                padding: 0.5rem 0.5rem;
            }
            .table-container {
                padding: 0;
            }
            .section-separator {
                margin: 24px 0;
            }
            h1 {
                font-size: 1.05em;
            }
            .rider-table {
                font-size: 0.95em;
            }
            .rider-table caption {
                font-size: 0.95em;
                margin-bottom: 0.3em;
            }
            .rider-table th,
            .rider-table td {
                font-size: 0.9em;
                padding: 5px 4px;
            }
            .footnote,
            .footnote-item {
                font-size: 0.9em;
            }
            .summary-footnote {
                font-size: 0.9em;
            }
        }
        /* --- Print: Optimized for paper, removes backgrounds, adjusts font sizes --- */
        @media print {
            body {
                background: #fff !important;
                color: #000 !important;
                margin: 0;
                padding: 0;
            }
            .table-container {
                overflow-x: visible !important;
                width: 100% !important;
                max-width: 100% !important;
                padding: 0 !important;
            }
            .section-separator {
                page-break-before: always;
            }
            h1 {
                color: #000 !important;
                font-size: 1.2em !important;
                margin-bottom: 0.75em !important;
            }
            .rider-table {
                font-size: 10pt !important;
                width: 100% !important;
                page-break-inside: avoid;
            }
            .rider-table caption {
                font-size: 1em !important;
                color: #000 !important;
                margin-bottom: 0.5em !important;
            }
            .rider-table th,
            .rider-table td {
                padding: 4px 4px !important;
                white-space: normal !important;
                background: none !important;
                color: #000 !important;
            }
            .rider-table th {
                border-bottom: 1px solid #444 !important;
                background: #eee !important;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }
            .rider-table tr:nth-child(even) td,
            .rider-table tr:hover td {
                background: none !important;
            }
            .footnote,
            .footnote-item {
                color: #000 !important;
                background: none !important;
                font-size: 0.85em !important;
            }
            .summary-footnote {
                color: #000 !important;
                background: none !important;
                font-size: 0.85em !important;
            }
            @page {
                size: A4 landscape;
                margin: 12mm 10mm 12mm 10mm;
            }
        }
    </style>
    """


