
def main(argv):
    scenarioBase = argv[0]

    shipmentSchemaFilePath = "/home/share/Code/cptl-models/data/schema/shipment.schema.v2.json"
    vesselShipmentSchema = None
    with open(shipmentSchemaFilePath) as shipmentSchemaFile:
        vesselShipmentSchema = json.load(shipmentSchemaFile)
    shipmentSchemaFile.close()

    # Loop through the shipments files
    commodityShipmentsInputFileBase = "/".join([scenarioBase, "flows/shipments"])

    
    
if __name__ == "__main__":
    main(sys.argv[1:])
