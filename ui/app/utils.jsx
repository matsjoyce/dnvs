// In JS we have sets. Which cannot be equality compared. Seriously.
export const isSetsEqual = (a, b) => a.size === b.size && [...a].every(value => b.has(value));
export const nullOrUndefined = x => x === null || x === undefined;
export const withDefault = (v, d) => nullOrUndefined(v) ? d : v;
export const ifNotNU = (v, f) => nullOrUndefined(v) ? v : f(v);
