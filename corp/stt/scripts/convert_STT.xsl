<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="2.0">

<!--  <xsl:output indent="no" method="xml"/>-->
  <xsl:output method="xml" indent="no"  encoding="UTF-8" omit-xml-declaration="no"/>

  <!--<xsl:key name="qcode_all" match="/newsItem/contentMeta/subject[@info='sttsubject']/@qcode" use="." />-->
  
  <xsl:template match="*">
    <xsl:copy>
      <xsl:for-each select="@*">
        <xsl:copy/>
      </xsl:for-each>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>

  <!-- Sort the articles by date -->
<!--  <xsl:template match="articles">
    <articles>
      <xsl:apply-templates>
        <xsl:sort select="newsItem/contentMeta/contentCreated"/>
      </xsl:apply-templates>
    </articles>
  </xsl:template> -->

  

  <xsl:template match="newsItem">
    <xsl:element name="text">
      <xsl:attribute name="filename"><xsl:value-of select="@guid"/></xsl:attribute>
      <xsl:attribute name="id"><xsl:value-of select="@guid"/></xsl:attribute>
      <xsl:attribute name="lang"><xsl:value-of select="@lang"/></xsl:attribute>
      <xsl:attribute name="provider"><xsl:value-of select="itemMeta/provider/@literal"/></xsl:attribute>
      <xsl:attribute name="embargoed_datetime"><xsl:value-of select="itemMeta/embargoed"/></xsl:attribute>
      <xsl:attribute name="publication_status"><xsl:value-of select="itemMeta/pubStatus/@qcode"/></xsl:attribute>
    <xsl:attribute name="editor_note"><xsl:value-of select="itemMeta/edNote[@role='sttnote:public']"/></xsl:attribute>
      <xsl:attribute name="news_urgency"><xsl:value-of select="contentMeta/urgency"/></xsl:attribute>
      <xsl:attribute name="datetime_orig"><xsl:value-of select="contentMeta/contentModified"/></xsl:attribute>
      <xsl:attribute name="date"><xsl:value-of select="contentMeta/contentModified"/></xsl:attribute>
      <xsl:attribute name="datetime_created"><xsl:value-of select="contentMeta/contentCreated"/></xsl:attribute>
      <!--<xsl:attribute name="located"><xsl:value-of select="contentMeta/located/name"/></xsl:attribute>-->
      <xsl:attribute name="location"><xsl:value-of select="assert/name"/></xsl:attribute>
      <xsl:attribute name="geo_latitude"><xsl:value-of select="assert/geoAreaDetails/position/@latitude"/></xsl:attribute>
      <xsl:attribute name="geo_longitude"><xsl:value-of select="assert/geoAreaDetails/position/@longitude"/></xsl:attribute>
      <xsl:attribute name="loc_address"><xsl:value-of select="assert/POIDetails/address/line"/></xsl:attribute>
      <xsl:attribute name="loc_postal_code"><xsl:value-of select="assert/POIDetails/address/postalCode"/></xsl:attribute>
      <xsl:attribute name="loc_city"><xsl:value-of select="assert/broader[@info='sttcity']/name"/></xsl:attribute>
      <xsl:attribute name="loc_state"><xsl:value-of select="assert/broader[@info='sttstate']/name"/></xsl:attribute>
      <xsl:attribute name="loc_country"><xsl:value-of select="assert/broader[@info='sttcountry']/name"/></xsl:attribute>
      <xsl:attribute name="loc_world_region"><xsl:value-of select="assert/broader[@info='wldreg']/name"/></xsl:attribute>
      <xsl:attribute name="news_department"><xsl:value-of select="contentMeta/subject[@info='sttdepartment']/name"/></xsl:attribute>
      <xsl:attribute name="news_department_code"><xsl:value-of select="contentMeta/subject[@info='sttdepartment']/@qcode"/></xsl:attribute>
      <xsl:attribute name="subjects_full"><xsl:for-each select="contentMeta/subject[@info='sttsubject']"><xsl:if test="@level='level1'"><xsl:text>|</xsl:text><xsl:value-of select="name"/></xsl:if><xsl:if test="@level='level2'"><xsl:text> &gt; </xsl:text><xsl:value-of select="name"/></xsl:if><xsl:if test="@level='level3'"><xsl:text> &gt; </xsl:text><xsl:value-of select="name"/></xsl:if></xsl:for-each><xsl:text>|</xsl:text></xsl:attribute>
      <xsl:attribute name="subjects_codes"><xsl:text>|</xsl:text><xsl:for-each select="contentMeta/subject[@info='sttsubject']"><xsl:value-of select="@qcode"/><xsl:text>|</xsl:text></xsl:for-each></xsl:attribute>
      <xsl:attribute name="subjects_level1"><xsl:text>|</xsl:text><xsl:for-each select="contentMeta/subject[@level='level1']"><xsl:value-of select="name"/><xsl:text>|</xsl:text></xsl:for-each></xsl:attribute>
      <xsl:attribute name="subjects_level1_codes"><xsl:text>|</xsl:text><xsl:for-each select="contentMeta/subject[@level='level1']"><xsl:value-of select="@qcode"/><xsl:text>|</xsl:text></xsl:for-each></xsl:attribute>
      <xsl:attribute name="subjects_level2"><xsl:text>|</xsl:text><xsl:for-each select="contentMeta/subject[@level='level2']"><xsl:value-of select="name"/><xsl:text>|</xsl:text></xsl:for-each></xsl:attribute>
      <xsl:attribute name="subjects_level2_codes"><xsl:text>|</xsl:text><xsl:for-each select="contentMeta/subject[@level='level2']"><xsl:value-of select="@qcode"/><xsl:text>|</xsl:text></xsl:for-each></xsl:attribute>
      <xsl:attribute name="subjects_level3"><xsl:text>|</xsl:text><xsl:for-each select="contentMeta/subject[@level='level3']"><xsl:value-of select="name"/><xsl:text>|</xsl:text></xsl:for-each></xsl:attribute>
      <xsl:attribute name="subjects_level3_codes"><xsl:text>|</xsl:text><xsl:for-each select="contentMeta/subject[@level='level3']"><xsl:value-of select="@qcode"/><xsl:text>|</xsl:text></xsl:for-each></xsl:attribute>
      <xsl:attribute name="author"><xsl:value-of select="contentMeta/by"/></xsl:attribute>
      <xsl:attribute name="author_orig"><xsl:value-of select="contentMeta/by"/></xsl:attribute>
      <xsl:attribute name="author_name_type">byline</xsl:attribute>

      <xsl:attribute name="headline"><xsl:value-of select="contentMeta/headline"/></xsl:attribute>
      <xsl:attribute name="creditline"><xsl:value-of select="contentMeta/creditline"/></xsl:attribute>
      <xsl:attribute name="creditline_orig"><xsl:value-of select="contentMeta/creditline"/></xsl:attribute>
      <xsl:attribute name="genre">news</xsl:attribute>
      <xsl:attribute name="news_genre"><xsl:value-of select="contentMeta/genre[@info='sttgenre']/name"/></xsl:attribute>
      <xsl:attribute name="news_genre_code"><xsl:value-of select="contentMeta/genre[@info='sttgenre']/@qcode"/></xsl:attribute>
      <xsl:attribute name="version"><xsl:value-of select="contentMeta/genre[@info='sttversion']/name"/></xsl:attribute>
      <xsl:attribute name="version_code"><xsl:value-of select="contentMeta/genre[@info='sttversion']/@qcode"/></xsl:attribute>
      <xsl:attribute name="keywords"><xsl:value-of select="contentMeta/keyword"/></xsl:attribute>
      <xsl:attribute name="charcount_orig"><xsl:value-of select="contentMeta/genre/related/@value"/></xsl:attribute>
      <xsl:attribute name="datefrom"><xsl:value-of select="contentMeta/contentModified"/></xsl:attribute>
      <xsl:attribute name="dateto"><xsl:value-of select="contentMeta/contentModified"/></xsl:attribute>
      <xsl:attribute name="timefrom"><xsl:value-of select="contentMeta/contentModified"/></xsl:attribute>
      <xsl:attribute name="timeto"><xsl:value-of select="contentMeta/contentModified"/></xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>


  <xsl:template match="itemMeta"/>

  <!--<xsl:template match="contentMeta"/>-->

  <xsl:template match="contentMeta">
    <xsl:choose>
      <xsl:when test="headline != ''">
	<paragraph type="heading" type_orig="headline">
	  <xsl:value-of select="headline"/>
	</paragraph>
      </xsl:when>
      <xsl:otherwise/>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="assert"/>

  <xsl:template match="contentSet">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="inlineXML">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="html">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="body">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="p">
    <xsl:choose>
      <xsl:when test="./h3">
	<paragraph type="heading" type_orig="h3">
	  <xsl:apply-templates/>
	</paragraph>
      </xsl:when>
      <xsl:otherwise>
	<paragraph type="text" type_orig="p">
	  <xsl:apply-templates/>
	</paragraph>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="h2">
    <paragraph type="heading" type_orig="h2">
      <xsl:apply-templates/>
    </paragraph>
  </xsl:template>

  <xsl:template match="h3">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="Person">
    <name type="person">
      <xsl:apply-templates/>
    </name>
  </xsl:template>

  <xsl:template match="Company">
    <name type="company">
      <xsl:apply-templates/>
    </name>
  </xsl:template>

  <xsl:template match="a">
    <xsl:element name="weblink">
      <xsl:attribute name="url">
	<xsl:value-of select="@href"/>
      </xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="b">
    <hi rend="bold">
      <xsl:apply-templates/>
    </hi>
  </xsl:template>

</xsl:stylesheet>
