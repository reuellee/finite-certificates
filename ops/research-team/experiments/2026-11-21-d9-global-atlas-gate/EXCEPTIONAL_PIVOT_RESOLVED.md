# D9 residual pivot exceptional branch excluded by uniformity (2026-11-21)

**Exact new lemma for one global residual factor; not full CAD.**

For `q=-bdi+bfg+cdh-ceg+cei-cfh`, let `P=ce-bd` and `R=bfg+cdh-ceg-cfh`, so `q=Pi+R`. On `P=0`, exact polynomial reduction gives `cR=(bg-ch)(cf-cd)` (equivalently, for c != 0, `R=(bg-ch)(f-d)`).

On the uniform normalized parent locus, `c != 0`. Also the parent bracket indexed by columns (0,2,4,6) is `d-f`, hence `f-d != 0`. Consequently `P=R=0` forces `bg-ch=0`. But the parent bracket indexed by columns (0,3,6,7) is `dh-eg`; using `ce=bd` and `bg=ch` gives `c(dh-eg)=d(ch-bg)=0`. This contradicts uniformity.

**Therefore `P=0` and `q=0` cannot occur simultaneously on any uniform parent realization cell.** The wall `q=0` is globally a rational graph `i=-R/P` on its actual uniform locus, with no exceptional branch. This corrects the previous report, which merely flagged the exceptional branch as potentially relevant.

This conclusion is **only for the displayed residual factor**. It does not establish that all 26,740 residual walls admit similarly unit pivots, nor enumerate global chambers. Original 9DVL ledger remains **2/9**.
