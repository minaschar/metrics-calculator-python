# Metrics

Every value this tool reports, with the formula **as implemented** -- which
is not always the textbook definition. This file is generated from
`metrics_calculator.registry`; run `python -m metrics_calculator.docs` to
refresh it.

Sources: Chidamber & Kemerer, *A Metrics Suite for Object Oriented Design*
(1994); Li & Henry, *Object-oriented metrics that predict maintainability*
(1993); Bansiya & Davis, *A hierarchical model for object-oriented design
quality assessment* (2002).

## Size

### LOC — Lines of Code

Non-blank lines spanned by the class body.

- **As implemented:** (last line - first line + 1) of the class node, minus blank lines in that span
- **Approximation:** Counts the whole class span including decorators and docstring; comment-only lines are not treated as blank.
- **Source:** Chidamber & Kemerer (1994)

### NOM — Number of Methods

Count of methods declared on the class.

- **As implemented:** number of distinct method names collected for the class
- **Approximation:** A method is any `def` or `async def` whose name appears in the class; functions nested inside a method body are counted too, and same-named definitions collapse to one.
- **Source:** Chidamber & Kemerer (1994)

### SIZE2 — Number of Properties and Methods

NOM plus the number of distinct fields.

- **As implemented:** NOM + WAC
- **Source:** Li & Henry (1993)

### WAC — Weighted Attributes per Class

Count of distinct class and instance fields.

- **As implemented:** number of distinct `self.x` / `ClassName.x` targets assigned anywhere in the class (plain, annotated or augmented assignment) plus class-body names
- **Approximation:** Field discovery is syntactic: only assignments are seen, not fields introduced only via `__slots__`, `setattr`, or a base class.
- **Source:** Li & Henry (1993)

### NOCC — Number of Children

Count of classes in the project that directly subclass this one.

- **As implemented:** number of project classes whose declared bases include this class's simple name
- **Approximation:** Bases are matched by simple name (`Foo`, or the last segment of `pkg.Foo`); a name clash between two unrelated classes will over-count.
- **Source:** Chidamber & Kemerer (1994)

## Complexity

### DIT — Depth of Inheritance Tree

Longest inheritance chain above this class, counting only project classes.

- **As implemented:** 0 if no base resolves to a project class, else 1 + max(DIT of resolved project bases); an inheritance cycle contributes 0
- **Approximation:** Bases from outside the analysed project (stdlib, third-party) do not add depth.
- **Source:** Chidamber & Kemerer (1994)

### WMPC1 — Weighted Methods per Class (complexity)

Average cyclomatic complexity per method.

- **As implemented:** round(total cyclomatic complexity / NOM, 2), or 0.0 when NOM is 0
- **Approximation:** Cyclomatic complexity is approximated as 1 per method plus 1 for each `if`/`for`/`while`/conditional-expression/comprehension clause and one per `match` case; `and`/`or`, `except` and `assert` are not counted.
- **Source:** Chidamber & Kemerer (1994)

### WMPC2 — Weighted Methods per Class (parameters)

NOM plus the total parameter count across all methods.

- **As implemented:** NOM + sum of positional parameter counts over all methods (`self` included)
- **Approximation:** Only positional parameters are counted; `*args`, `**kwargs` and keyword-only parameters are ignored.
- **Source:** Chidamber & Kemerer (1994)

### RFC — Response for a Class

NOM plus the number of distinct methods of other classes called from this one.

- **As implemented:** NOM + number of distinct (receiver name, method name) pairs called on other objects
- **Approximation:** Remote calls are matched by method name only (no type resolution); a call counts if any project class defines a method of that name.
- **Source:** Chidamber & Kemerer (1994)

## Coupling

### CBO — Coupling Between Objects

Number of other classes this class is coupled to via method calls or inheritance.

- **As implemented:** count of distinct names in (receivers of remote calls) plus (declared base names), then + NOCC
- **Approximation:** Coupling partners are approximated by the *names* used at call sites and in `class Foo(Bar)` clauses, not by resolved classes, so a local variable and an unrelated class sharing a name are conflated.
- **Source:** Chidamber & Kemerer (1994)

### MPC — Message-Passing Coupling

Count of calls this class makes to methods of other classes.

- **As implemented:** number of `receiver.method(...)` call sites where `method` is defined by some project class and the receiver is not `self` or the class itself
- **Approximation:** Unlike RFC this is call sites, not distinct methods. Attribute reads that are not calls (`f(obj.attr)`) are not counted.
- **Source:** Li & Henry (1993)

## Cohesion

### LCOM — Lack of Cohesion in Methods

Non-cohesive minus cohesive method pairs (by shared field use), floored at zero.

- **As implemented:** max(P - Q, 0) where, over unordered method pairs, Q share at least one field and P share none
- **Approximation:** Only fields already known for the class count as shared use, and only attribute accesses in the method's own body -- nested functions and classes are excluded.
- **Source:** Chidamber & Kemerer (1994) / Sharble & Cohen

## Project-level

### NOC — Number of Classes

Total number of classes found across the analyzed project.

- **As implemented:** count of class definitions discovered in all analysed files
- **Approximation:** A class defined inside a method body is counted twice, matching the original tool's discovery.
- **Source:** Chidamber & Kemerer (1994)

## QMOOD design attributes (not implemented)

### Reusability

Declared by the original tool but never computed; kept here as documented future work.

- **Status:** not computed by this release.
- **Source:** Bansiya & Davis (2002)

### Flexibility

Declared by the original tool but never computed; kept here as documented future work.

- **Status:** not computed by this release.
- **Source:** Bansiya & Davis (2002)

### Understandability

Declared by the original tool but never computed; kept here as documented future work.

- **Status:** not computed by this release.
- **Source:** Bansiya & Davis (2002)

### Functionality

Declared by the original tool but never computed; kept here as documented future work.

- **Status:** not computed by this release.
- **Source:** Bansiya & Davis (2002)

### Extendability

Declared by the original tool but never computed; kept here as documented future work.

- **Status:** not computed by this release.
- **Source:** Bansiya & Davis (2002)

### Effectiveness

Declared by the original tool but never computed; kept here as documented future work.

- **Status:** not computed by this release.
- **Source:** Bansiya & Davis (2002)
