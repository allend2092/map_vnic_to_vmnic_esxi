# map_vnic_to_vmnic_esxi
map_vnic_to_vmnic_esxi


Code should be run something like this:
python3 ./map_vnic_to_pnic.py -f credentials.json inventory.txt

Output to the screen looks something like this:
VM Name: nsx-t-manager1, World ID: 2100916
VM Name: Ubuntu-SFTP, World ID: 2101121
VM Name: UPSA913s-Test-02, World ID: 2101313
VM Name: vCLS-11e83154-129d-4558-acae-61c60e4dd0df, World ID: 2101846
VM Name: vCLS-6ffef583-94b9-40f5-8179-b8d26876b762, World ID: 2101167
VM Name: Windows-Server-2012-R2, World ID: 2100909
VM Name: vcenter, World ID: 2101090
VM Name: vCLS-4dba3e7f-30fc-4e3a-bed9-7896476c194c, World ID: 2101674

The code produces an output.json file looking something like this:
{
    "nsx-t-manager1": [
        {
            "MAC Address": "00:50:56:b3:c4:ed",
            "vmnic": "vmnic2",
            "Portgroup": "dvportgroup-1004",
            "Port ID": "67108885"
        }
    ],
    "Ubuntu-SFTP": [
        {
            "MAC Address": "00:50:56:b3:9d:16",
            "vmnic": "vmnic2",
            "Portgroup": "dvportgroup-1004",
            "Port ID": "67108884"
        }
    ],
    "UPSA913s-Test-02": [
        {
            "MAC Address": "00:50:56:b3:c4:bd",
            "vmnic": "vmnic2",
            "Portgroup": "dvportgroup-1004",
            "Port ID": "67108886"
        },
        {
            "MAC Address": "00:50:56:b3:59:7c",
            "vmnic": "vmnic3",
            "Portgroup": "VM Network",
            "Port ID": "100663315"
        }
    ],
    "Windows-Server-2012-R2": [
        {
            "MAC Address": "00:0c:29:a9:0e:ec",
            "vmnic": "vmnic2",
            "Portgroup": "dvportgroup-1005",
            "Port ID": "67108880"
        }
    ],
    "vcenter": [
        {
            "MAC Address": "00:0c:29:23:b8:6c",
            "vmnic": "vmnic2",
            "Portgroup": "dvportgroup-1004",
            "Port ID": "67108879"
        }
    ]
}
