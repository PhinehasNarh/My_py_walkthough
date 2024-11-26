network_devices=['cisco1','fortinet2','aS4D7','linksys8','nETGEAR04','nETGEAR05']


#extending(adds the string elemnts)
new_devices=['router5','moderm2']
network_devices.extend(new_devices)
print(network_devices)

#sorting(sorts according in ascending order)
network_devices.sort()
print(network_devices)

#counting(counts how many times each string element appeared )
print(network_devices.count('nETGEAR05'))

#indexing(shows the number position according to how its listed/sorted)
network_item=network_devices.index('fortinet2')
print(network_item)
#or 
#can use this instead, looks pretty easy to me,prefer this one more 
print(network_devices[7])

#range(diplays the range of lements within a list)
print(network_devices[1:6])


#inserting a string into a list and specifying its position
print(network_devices.insert(4,'linksys12'))
print(network_devices)


#reversing the whole list backwards
network_devices.reverse()
print(network_devices)

#clear the whole elements in the list to an empty list
network_devices.clear()
print(network_devices)



storage_devices=['pendrive','harddisk']
network_devices.extend(storage_devices)
print(network_devices)


x=range(0,10,2)
for n in x:
    print(n)


#ph1n3y
