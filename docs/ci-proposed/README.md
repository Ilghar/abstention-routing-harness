# CI: proposed, blocked (M08)

**Decision: GitHub Actions was not enabled.** Per the owner's rule, workflows may run only once it is verified that paid overage is impossible, for example a $0 Actions budget or no payment method on file.

## Evidence gathered (read-only, 2026-10-25)
- The GitHub connector's `get_me` returns only public profile fields (login Ilghar, type User). It returns no plan, payment-method, budget or usage fields.
- Neither available connector exposes a billing, budget or Actions-usage endpoint. Billing settings were not opened and not changed.
- GitHub docs (docs.github.com/en/billing/concepts/product-billing/github-actions): private repos get a plan-dependent quota of free minutes, and usage beyond it is billed to the owner. *"If your account does not have a valid payment method on file, usage is blocked once you use up your quota"*. With a payment method, spending is limited only by whatever budgets are configured.
- So whether overage can occur depends on the payment method and budget state, and neither could be observed. **Status: unverifiable, so CI is blocked.**

## Cost bound if enabled
One manual-only Linux job with `timeout-minutes: 5`. The local suite takes under 10 s and the example under 10 s. GitHub lists the Linux 2-core rate at $0.006/min, so a run that hits the 5-minute cap would cost at most about $0.03 beyond the free quota.

## To unblock (owner action, outside this coordinator)
Check under Settings → Billing and licensing that the Actions budget is $0 with "stop usage" on, or that no payment method is on file. Then copy `ci.yml` to `.github/workflows/ci.yml`.
