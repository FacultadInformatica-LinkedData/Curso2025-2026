<img width="1817" height="2137" alt="JDCusme-JesúsCusme" src="https://github.com/user-attachments/assets/09259a15-a27a-4d56-bf1f-62216506f9cb" />{
  "@context": {
    "schema": "http://schema.org/",
    "ex": "http://example.org/",
    "name": "schema:name",
    "hometown": "schema:homeLocation",
    "age": "schema:age",
    "almaMater": "schema:alumniOf",
    "parents": "schema:parent",
    "subjects": "ex:enrolledIn",
    "subjectName": "schema:name",
    "teachers": "ex:taughtBy",
    "description": "schema:description"
  },
  "@type": "schema:Person",
  "@id": "ex:Jesus",
  "name": "Jesus Daniel Cusme Gavilanez",
  "hometown": "Almería",
  "age": 21,
  "almaMater": "ETSIINF UPM",
  "parents": [
    "Lucia",
    "Jesús"
  ],
  "subjects": [
    {
      "@type": "schema:Course",
      "subjectName": "Semantic Web, Linked Data and Knowledge Graphs",
      "teachers": [
        "Oscar Corcho Garcia"
      ],
      "description": "Study the data on the Web of Linked Data, as well as knowledge graphs"
    }
  ]
}

{
  "@context": {
    "ex": "http://example.org/",
    "includes": "ex:includes",
    "hasMeasurement": "ex:hasMeasurement",
    "hasTemperature": "ex:hasTemperature",
    "atTime": "ex:atTime",
    "hasOwner": "ex:hasOwner",
    "hasName": "ex:hasName"
  },
  "@graph": [
    {
      "@id": "ex:Class01",
      "@type": "ex:Class",
      "includes": [
        {
          "@id": "ex:Sensor029"
        },
        {
          "@id": "ex:Computer101"
        }
      ]
    },
    {
      "@id": "ex:Sensor029",
      "@type": "ex:Sensor",
      "hasMeasurement": {
        "@id": "ex:Measurement8401"
      }
    },
    {
      "@id": "ex:Measurement8401",
      "@type": "ex:Measurement",
      "hasTemperature": 29,
      "atTime": "2010-06-12T12:00:12"
    },
    {
      "@id": "ex:Computer101",
      "@type": "ex:Computer",
      "hasOwner": {
        "@id": "ex:User10A"
      }
    },
    {
      "@id": "ex:User10A",
      "@type": "ex:User",
      "hasName": "Pedro"
    }
  ]
}

@base <http://example.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex: <http://example.org/> .
@prefix et: <http://example.org/et#> .

<ClassRoom03> rdf:type ex:ClassRoom ;
    ex:contains <Sensor047> ;
    ex:contains <Table322> .

<Sensor047> rdf:type ex:Sensor ;
    ex:hasMeasurement <Measurement> .

<Measurement> rdf:type ex:Measurement ;
    ex:hasMeasurementID23 <MeasurementID23> ;
    ex:hasSensorID <Sensor047> .
<MeasurementID23> rdf:type ex:MeasurementID ;
    rdf:value "2022-08-*/21 14:21:12" .
    
<Table322> rdf:type ex:Table ;
    ex:hasOwner et:Informations .

et:Informations rdf:type et:Information ;
    ex:hasName "ET:Id-Informations" .

  <img width="1817" height="2137" alt="JDCusme-JesúsCusme" src="https://github.com/user-attachments/assets/a83bf81b-77d0-40b3-b532-20b4413de692" />
  
