# encoding: utf-8
import sys, getopt, os, time, threading
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
archiveConfiguration = 'Release' # 打包的配置，一般区分Debug和Release
provisioning_profile = "\"iOS Team Provisioning Profile: *\"" # 证书名，不是证书文件名，两者是不同的
workspace = "../test.xcworkspace" #工作空间
scheme = "test"        # scheme 名
archivePath = "../build/test-%s.xcarchive" % (time)  # 归档路径
exportPath = "../build/test-%s.ipa" % (time)  # 导出IPA的路径

upload = "yes"   # 是否上传蒲公英

# 蒲公英用户配置，不同用户不同
pgyer_uKey_li = "A"
pgyer_apiKey_li = "A"

pgyer_uKey_lei = "B"
pgyer_apiKey_lei = "B"

pgyer_uKey_zhao = "C"
pgyer_apiKey_zhao = "C"

pgyer_uKey_team = "D"
pgyer_apiKey_team = "D"

pgyer_uKey = pgyer_uKey_lei
pgyer_apiKey = pgyer_apiKey_lei

# bundleName 和 bundleID 配置，用于打不同的包
bundleDisplayName_li = u'li'
bundleProductID_li = u'com.test.li'

bundleDisplayName_lei = u'lei'
bundleProductID_lei = u'com.test.lei'

bundleDisplayName_zhao = u'zhao'
bundleProductID_zhao = u'com.test.zhao'

bundleDisplayName_team = u'team'
bundleProductID_team = u'com.test.team'

bundleDisplayName = bundleDisplayName_team
bundleProductID = bundleProductID_team

developer = 'team'

infolist = '../test/Info.plist'
copy_infolist = '../test/_Info.plist'


def main(argv):
    # 移除build目录
    # os.system("rm -r -f ../build")

    global archiveConfiguration
    global workspace
    global provisioning_profile
    global scheme
    global archivePath
    global exportPath
    global pgyer_uKey
    global pgyer_apiKey
    global upload
    global developer
    global bundleProductID
    global bundleDisplayName
    global pgyer_uKey
    global pgyer_apiKey

    shortargs = 'c'
    longargs = ['workspace', 'provisioning_profile', 'archivePath', 'exportPath', 'pgyer_uKey', 'pgyer_apiKey',
                'scheme', 'upload', 'li','lei','zhao']
    opts, args = getopt.getopt(argv[1:], shortargs, longargs)
    for op, value in opts:
        if op == "-c":
            archiveConfiguration = value
        elif op == "--workspace":
            workspace = value
        elif op == "--provisioning_profile":
            provisioning_profile = value
        elif op == "--scheme":
            scheme = value
        elif op == "--archivePath":
            archivePath = value
        elif op == "--exportPath":
            exportPath = value
        elif op == "--pgyer_uKey":
            pgyer_uKey = value
        elif op == "--pgyer_apiKey":
            pgyer_apiKey = value
        elif op == "--upload":
            upload = value
        elif op == "--li":
            developer = 'li'
        elif op == "--lei":
             developer = 'lei'
        elif op == "--zhao":
                        developer = 'zhao'

    print "任务0 - 更改bundleId和bundleName"

    os.rename(infolist,copy_infolist)

    if developer == "team":
        bundleDisplayName = bundleDisplayName_team
        bundleProductID = bundleProductID_team
        pgyer_apiKey = pgyer_apiKey_team
        pgyer_uKey = pgyer_uKey_team
    elif developer == "li":
        bundleDisplayName = bundleDisplayName_li
        bundleProductID = bundleProductID_li
        pgyer_apiKey = pgyer_apiKey_li
        pgyer_uKey = pgyer_uKey_li
    elif developer == "lei":
        bundleDisplayName = bundleDisplayName_lei
        bundleProductID = bundleProductID_lei
        pgyer_apiKey = pgyer_apiKey_lei
        pgyer_uKey = pgyer_uKey_lei
    elif developer == "zhao":
        bundleDisplayName = bundleDisplayName_zhao
        bundleProductID = bundleProductID_zhao
        pgyer_apiKey = pgyer_apiKey_zhao
        pgyer_uKey = pgyer_uKey_zhao

    print "准备对bundleId为: " + bundleProductID.encode('utf-8') + "   bundleName为：" + bundleDisplayName.encode('utf-8') + "  进行打包"
    threading._sleep(2)
    print "Begin Archieve"
    
    utf8_parser = ET.XMLParser(encoding='utf-8')
    tree = ET.parse(copy_infolist, parser=utf8_parser)
    
    root = tree.getroot()
    
    dict = root[0]
    
    for child in dict:
        childText = child.text
        if childText != None:
            if u'test' in childText:
                childText = bundleDisplayName
            
            elif childText == u'$(PRODUCT_NAME)':
                childText = bundleDisplayName
            
            elif childText == u'$(PRODUCT_BUNDLE_IDENTIFIER)':
                childText = bundleProductID
            
            child.text = childText
    tree.write(infolist, encoding='utf-8')
    
    print "任务1 - 归档"
    os.system("xcodebuild -workspace %s -sdk iphoneos -scheme %s -archivePath %s -configuration %s archive" % (workspace, scheme, archivePath, archiveConfiguration))
    print "任务2 - 导出IPA"
    os.system("xcodebuild  -exportArchive -exportFormat IPA -archivePath %s -exportPath %s -exportProvisioningProfile %s" % (archivePath, exportPath, provisioning_profile))

    if upload == "yes":
        print "任务3 - 上传蒲公英"
        os.system("curl -F \"file=@%s\" -F \"uKey=%s\" -F \"_api_key=%s\" http://www.pgyer.com/apiv1/app/upload" % (exportPath, pgyer_uKey, pgyer_apiKey))
        os.remove(infolist)
        os.rename(copy_infolist,infolist)

if __name__ == '__main__':
    main(sys.argv)