// Every body that the mock server answers with matches its schema in the
// server's contract, brown_field/spec/openapi.yaml. A mock that drifts from
// the real server fails here, not silently in a component test.
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import yaml from "js-yaml";
import { describe, expect, it } from "vitest";
import { CONTRACT_SAMPLES } from "./bodies";

// Vitest runs from brown_field/web; the contract is in brown_field/spec.
const contractPath = resolve(process.cwd(), "../spec/openapi.yaml");
const contract = yaml.load(readFileSync(contractPath, "utf-8")) as { components: { schemas: Record<string, unknown> } };

const ajv = new Ajv2020({ strict: false, allErrors: true });
addFormats(ajv);
ajv.addSchema({ $id: "openapi", components: contract.components });

describe("the mock bodies match the server's contract", () => {
  it.each(CONTRACT_SAMPLES.map(([schema, body], index) => [`${index}: ${schema}`, schema, body] as const))(
    "%s",
    (_label, schema, body) => {
      const validate = ajv.getSchema(`openapi#/components/schemas/${schema}`)!;
      expect(validate, `no schema ${schema}`).toBeDefined();
      expect(validate(body), JSON.stringify(validate.errors)).toBe(true);
    },
  );

  it("rejects a body that the contract does not allow", () => {
    const validate = ajv.getSchema("openapi#/components/schemas/Location")!;
    expect(validate({ title: "BRICK LANE" })).toBe(false);
  });
});
